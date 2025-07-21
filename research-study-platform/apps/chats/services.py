import openai
from django.conf import settings
from .models import ChatInteraction, ChatSession
import time
import logging
import json
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import redis
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RateLimitManager:
    """Manages OpenAI API rate limiting"""
    
    def __init__(self):
        try:
            self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
            # Test the connection
            self.redis_client.ping()
            logger.info("Redis client initialized successfully")
        except Exception as e:
            self.redis_client = None
            logger.warning(f"Redis not available, rate limiting will be disabled: {str(e)}")
    
    def check_rate_limit(self, user_id: str) -> Tuple[bool, int]:
        """Check if user has exceeded rate limits"""
        if not self.redis_client:
            return True, 0
        
        try:
            # Check requests per minute
            requests_key = f"openai_requests:{user_id}:{datetime.now().strftime('%Y-%m-%d:%H:%M')}"
            current_requests = self.redis_client.get(requests_key)
            current_requests = int(current_requests) if current_requests else 0
            
            if current_requests >= settings.OPENAI_RATE_LIMIT_REQUESTS:
                return False, settings.OPENAI_RATE_LIMIT_REQUESTS - current_requests
            
            # Increment counter
            self.redis_client.incr(requests_key)
            self.redis_client.expire(requests_key, 60)  # Expire after 1 minute
            
            return True, settings.OPENAI_RATE_LIMIT_REQUESTS - current_requests - 1
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True, 0
    
    def add_token_usage(self, user_id: str, tokens: int):
        """Track token usage for rate limiting"""
        if not self.redis_client:
            return
        
        try:
            tokens_key = f"openai_tokens:{user_id}:{datetime.now().strftime('%Y-%m-%d:%H:%M')}"
            self.redis_client.incr(tokens_key, tokens)
            self.redis_client.expire(tokens_key, 60)  # Expire after 1 minute
        except Exception as e:
            logger.error(f"Token tracking failed: {e}")


class OpenAIService:
    
    LINUX_SYSTEM_PROMPT = """You are a helpful, knowledgeable, and friendly AI assistant. You can help with any topic or question the user asks about.

    **Your Capabilities:**
    - Answer questions on any subject
    - Provide explanations, advice, and guidance
    - Help with problem-solving and analysis
    - Offer creative assistance and brainstorming
    - Engage in casual conversation
    - Assist with learning and education on any topic

    **Response Style:**
    - Be helpful, accurate, and informative
    - Adapt your tone and complexity to the user's needs
    - Provide practical examples when relevant
    - Be conversational and engaging
    - Offer multiple perspectives when appropriate
    - Be honest about limitations or uncertainty

    Feel free to ask me about anything - from everyday questions to complex topics, creative projects, personal advice, or just having a conversation. I'm here to help with whatever you need!"""
    
    # OpenAI pricing per 1K tokens (as of 2024)
    PRICING = {
        'gpt-4': {'input': 0.03, 'output': 0.06},
        'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
        'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002},
    }
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        if not self.api_key:
            logger.warning("OpenAI API key not configured")
            self.client = None
        else:
            try:
                # Set API key as environment variable to avoid parameter issues
                import os
                os.environ['OPENAI_API_KEY'] = self.api_key
                
                # Initialize with no parameters - let OpenAI use env var
                self.client = openai.OpenAI()
                logger.info("OpenAI client initialized successfully with environment variable")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")
                self.client = None
        
        self.rate_limiter = RateLimitManager()
        self.model = getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo')
        self.max_tokens = getattr(settings, 'OPENAI_MAX_TOKENS', 150)
        self.temperature = getattr(settings, 'OPENAI_TEMPERATURE', 0.7)
    
    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> Decimal:
        """Calculate estimated cost for API call"""
        if model not in self.PRICING:
            model = 'gpt-3.5-turbo'  # Default fallback
        
        pricing = self.PRICING[model]
        input_cost = (prompt_tokens / 1000) * pricing['input']
        output_cost = (completion_tokens / 1000) * pricing['output']
        
        return Decimal(str(input_cost + output_cost))
    
    def validate_response(self, response_content: str) -> Tuple[bool, str]:
        """Validate response content with minimal restrictions"""
        # Always allow responses - no content restrictions
        # This ensures ChatGPT can respond to any topic naturally
        return True, "Response is valid"
    
    def generate_response(self, messages: List[Dict], user_id: str, retry_count: int = 0) -> Dict:
        """Generate response from OpenAI API with comprehensive error handling"""
        
        # Check if OpenAI client is available
        if not self.client:
            return self._generate_fallback_response(messages, retry_count)
        
        # Check rate limiting
        can_proceed, remaining_requests = self.rate_limiter.check_rate_limit(user_id)
        if not can_proceed:
            return {
                'content': "Rate limit exceeded. Please wait a moment before sending another message.",
                'response_time_ms': 0,
                'prompt_tokens': 0,
                'completion_tokens': 0,
                'total_tokens': 0,
                'success': False,
                'error': 'Rate limit exceeded',
                'model': self.model,
                'rate_limit_hit': True,
                'retry_count': retry_count
            }
        
        # Add system prompt
        system_message = {'role': 'system', 'content': self.LINUX_SYSTEM_PROMPT}
        full_messages = [system_message] + messages
        
        try:
            start_time = time.time()
            
            # Ensure we only pass supported parameters to avoid "proxies" error
            completion_params = {
                'model': self.model,
                'messages': full_messages,
                'max_tokens': self.max_tokens,
                'temperature': self.temperature,
            }
            
            logger.debug(f"Making OpenAI API call with model: {self.model}")
            response = self.client.chat.completions.create(**completion_params)
            
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            content = response.choices[0].message.content
            usage = response.usage
            
            # Validate response
            is_valid, validation_message = self.validate_response(content)
            if not is_valid:
                logger.warning(f"Invalid response detected: {validation_message}")
                content = "I can only help with these Linux commands: ls, cd, pwd, cat, cp, mv, chmod, chown, grep, find. Please ask about one of these commands."
            
            # Calculate cost
            estimated_cost = self.calculate_cost(self.model, usage.prompt_tokens, usage.completion_tokens)
            
            # Track token usage
            self.rate_limiter.add_token_usage(user_id, usage.total_tokens)
            
            return {
                'content': content,
                'response_time_ms': response_time_ms,
                'prompt_tokens': usage.prompt_tokens,
                'completion_tokens': usage.completion_tokens,
                'total_tokens': usage.total_tokens,
                'success': True,
                'model': self.model,
                'estimated_cost': estimated_cost,
                'rate_limit_hit': False,
                'retry_count': retry_count,
                'api_request_id': getattr(response, 'id', ''),
                'validation_passed': is_valid
            }
        
        except openai.RateLimitError as e:
            logger.warning(f"OpenAI rate limit error: {str(e)}")
            return {
                'content': "I'm currently experiencing high demand. Please try again in a moment.",
                'response_time_ms': 0,
                'prompt_tokens': 0,
                'completion_tokens': 0,
                'total_tokens': 0,
                'success': False,
                'error': 'OpenAI rate limit',
                'model': self.model,
                'rate_limit_hit': True,
                'retry_count': retry_count
            }
        
        except openai.AuthenticationError as e:
            logger.error(f"OpenAI authentication error: {str(e)}")
            return {
                'content': "I'm sorry, there's a configuration issue. Please contact support.",
                'response_time_ms': 0,
                'prompt_tokens': 0,
                'completion_tokens': 0,
                'total_tokens': 0,
                'success': False,
                'error': 'Authentication error',
                'model': self.model,
                'rate_limit_hit': False,
                'retry_count': retry_count
            }
        
        except openai.APITimeoutError as e:
            logger.error(f"OpenAI timeout error: {str(e)}")
            if retry_count < 2:  # Retry up to 2 times
                time.sleep(1)  # Wait 1 second before retry
                return self.generate_response(messages, user_id, retry_count + 1)
            
            return {
                'content': "I'm sorry, the request timed out. Please try again.",
                'response_time_ms': 0,
                'prompt_tokens': 0,
                'completion_tokens': 0,
                'total_tokens': 0,
                'success': False,
                'error': 'Timeout error',
                'model': self.model,
                'rate_limit_hit': False,
                'retry_count': retry_count
            }
        
        except TypeError as e:
            error_msg = str(e)
            logger.error(f"OpenAI TypeError (possibly 'proxies' argument): {error_msg}")
            
            # Handle specific proxies argument error
            if 'proxies' in error_msg:
                logger.error("Detected 'proxies' argument error. Client may need reinitialization.")
                try:
                    # Try to reinitialize client without any optional parameters
                    self.client = openai.OpenAI(api_key=self.api_key)
                    logger.info("Client reinitialized successfully")
                    
                    # Retry the API call once
                    if retry_count < 1:
                        return self.generate_response(messages, user_id, retry_count + 1)
                except Exception as reinit_error:
                    logger.error(f"Failed to reinitialize client: {str(reinit_error)}")
            
            return {
                'content': "I'm sorry, there's a technical issue with the chat service. Please try again.",
                'response_time_ms': 0,
                'prompt_tokens': 0,
                'completion_tokens': 0,
                'total_tokens': 0,
                'success': False,
                'error': f'TypeError: {error_msg}',
                'model': self.model,
                'rate_limit_hit': False,
                'retry_count': retry_count
            }
        
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            return {
                'content': f"I'm sorry, I encountered an error. Please try again later.",
                'response_time_ms': 0,
                'prompt_tokens': 0,
                'completion_tokens': 0,
                'total_tokens': 0,
                'success': False,
                'error': str(e),
                'model': self.model,
                'rate_limit_hit': False,
                'retry_count': retry_count
            }
    
    def build_conversation_history(self, session, max_turns=10):
        """Build conversation history for context"""
        interactions = ChatInteraction.objects.filter(
            session=session,
            message_type__in=['user_message', 'assistant_response']
        ).order_by('-conversation_turn')[:max_turns * 2]
        
        messages = []
        for interaction in reversed(interactions):
            if interaction.message_type == 'user_message' and interaction.user_message:
                messages.append({
                    'role': 'user',
                    'content': interaction.user_message
                })
            elif interaction.message_type == 'assistant_response' and interaction.assistant_response:
                messages.append({
                    'role': 'assistant',
                    'content': interaction.assistant_response
                })
        
        return messages
    
    def create_chat_interaction(self, session, user_message, conversation_turn=1):
        """Create and process a chat interaction"""
        try:
            # Create user message interaction
            user_interaction = ChatInteraction.objects.create(
                session=session,
                user=session.user,
                message_type='user_message',
                user_message=user_message,
                conversation_turn=conversation_turn
            )
            
            # Only generate response for CHATGPT group
            if session.user.study_group != 'CHATGPT':
                return {
                    'success': False,
                    'error': 'Chat functionality is only available for CHATGPT group',
                    'user_interaction': user_interaction
                }
            
            # Build conversation history
            conversation_history = self.build_conversation_history(session)
            
            # Add current user message
            conversation_history.append({
                'role': 'user',
                'content': user_message
            })
            
            # Generate response
            response_data = self.generate_response(conversation_history, str(session.user.id))
            
            if response_data['success']:
                # Create assistant response interaction
                assistant_interaction = ChatInteraction.objects.create(
                    session=session,
                    user=session.user,
                    message_type='assistant_response',
                    assistant_response=response_data['content'],
                    conversation_turn=conversation_turn,
                    response_time_ms=response_data['response_time_ms'],
                    openai_model=response_data['model'],
                    prompt_tokens=response_data['prompt_tokens'],
                    completion_tokens=response_data['completion_tokens'],
                    total_tokens=response_data['total_tokens'],
                    estimated_cost_usd=response_data.get('estimated_cost', 0),
                    api_request_id=response_data.get('api_request_id', ''),
                    rate_limit_hit=response_data.get('rate_limit_hit', False),
                    retry_count=response_data.get('retry_count', 0)
                )
                
                # Update conversation history in user interaction
                user_interaction.conversation_history = conversation_history
                user_interaction.save()
                
                return {
                    'success': True,
                    'user_interaction': user_interaction,
                    'assistant_interaction': assistant_interaction,
                    'response_data': response_data
                }
            else:
                # Create error interaction
                error_interaction = ChatInteraction.objects.create(
                    session=session,
                    user=session.user,
                    message_type='error',
                    error_message=response_data['error'],
                    conversation_turn=conversation_turn,
                    rate_limit_hit=response_data.get('rate_limit_hit', False),
                    retry_count=response_data.get('retry_count', 0)
                )
                
                return {
                    'success': False,
                    'error': response_data['error'],
                    'user_interaction': user_interaction,
                    'error_interaction': error_interaction
                }
        
        except Exception as e:
            logger.error(f"Error creating chat interaction: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_fallback_response(self, messages: List[Dict], retry_count: int) -> Dict:
        """Generate intelligent fallback response when OpenAI API is not available"""
        if not messages:
            content = "Hello! I'm your AI assistant. I can help you with any questions about Linux commands and more. What would you like to know?"
        else:
            last_message = messages[-1]['content'].lower()
            content = self._get_intelligent_response(last_message)
        
        return {
            'content': content,
            'response_time_ms': 100,
            'prompt_tokens': 50,
            'completion_tokens': len(content.split()) * 1.3,
            'total_tokens': 50 + len(content.split()) * 1.3,
            'success': True,
            'error': '',
            'model': self.model,
            'rate_limit_hit': False,
            'retry_count': retry_count,
            'estimated_cost': Decimal('0.001')
        }
    
    def _get_intelligent_response(self, user_input: str) -> str:
        """Generate intelligent response to user's question"""
        
        # Example requests (check first)
        if any(word in user_input for word in ['example', 'examples', 'show me', 'give', 'demonstrate']):
            import random
            examples = [
                """Here are some practical Linux command examples:

**File Management:**
- `ls -la ~/Documents` - List all files in Documents with details
- `cp important.txt backup/` - Copy file to backup folder
- `mv downloads/*.pdf ~/Documents/PDFs/` - Move all PDFs to Documents

**Text Operations:**  
- `grep -r "TODO" src/` - Find all TODO comments in source code
- `find . -name "*.log" -size +1M` - Find log files larger than 1MB
- `cat error.log | grep "ERROR" | tail -10` - Show last 10 error messages

What specific command would you like examples for?""",

                """Here are some useful Linux command combinations:

**System Information:**
- `ls -lh /var/log/` - Check log file sizes
- `find /home -name "*.tmp" -delete` - Clean up temp files
- `chmod +x script.sh && ./script.sh` - Make script executable and run it

**File Search & Organization:**
- `grep -n "function" *.py` - Find functions in Python files with line numbers
- `cp -r project/ backup/project-$(date +%Y%m%d)` - Backup with timestamp
- `find . -type f -name "*.txt" | head -5` - Show first 5 text files

Which type of examples interest you most?""",

                """Here are some beginner-friendly Linux examples:

**Getting Started:**
- `pwd` then `ls` - See where you are and what's there
- `cd Desktop && ls` - Go to Desktop and see what's on it
- `cat README.txt` - Read a text file

**Safe Practice:**
- `cp file.txt file.txt.backup` - Always backup before editing
- `ls -la` before `rm` - Check what you're about to delete
- `chmod +x script` then `ls -l script` - Verify permissions changed

Want to learn about any specific command in detail?"""
            ]
            return random.choice(examples)

        # Common question patterns (check before specific commands)
        elif any(word in user_input for word in ['difference', 'compare', 'vs', 'versus']):
            return """Great question about comparing commands! Here are key differences:

**cp vs mv:**
- `cp` copies (original stays), `mv` moves (original gone)
- `cp file.txt backup.txt` - Now you have both files
- `mv file.txt renamed.txt` - file.txt no longer exists

**chmod vs chown:**  
- `chmod` changes permissions (read/write/execute)
- `chown` changes ownership (which user owns the file)

**grep vs find:**
- `grep` searches INSIDE files for text content
- `find` searches FOR files by name, size, date, etc.

**ls vs pwd:**
- `ls` shows WHAT'S in your current directory
- `pwd` shows WHERE your current directory is located

What specific comparison were you curious about?"""

        elif any(word in user_input for word in ['how do i', 'how to', 'how can i']):
            return """Great question! I can help you with Linux commands. Here are some common "how to" scenarios:

**File Operations:**
- "How do I list files?" → Use `ls` or `ls -la` for detailed view
- "How do I copy files?" → Use `cp source destination`  
- "How do I move files?" → Use `mv source destination`

**Navigation:**
- "How do I change directories?" → Use `cd /path/to/directory`
- "How do I see where I am?" → Use `pwd`

**File Content:**
- "How do I view file contents?" → Use `cat filename.txt`
- "How do I search in files?" → Use `grep "pattern" filename`

What specific task are you trying to accomplish?"""

        elif any(word in user_input for word in ['what is', 'what does', 'explain']):
            return """I can explain any of the Linux commands! Here's what each one does:

**File Listing & Navigation:**
- `ls` - Shows files and directories in current location
- `cd` - Changes your current directory
- `pwd` - Shows your current directory path

**File Operations:**
- `cat` - Displays file contents on screen  
- `cp` - Copies files or directories
- `mv` - Moves or renames files/directories

**Permissions & Ownership:**
- `chmod` - Changes file permissions (who can read/write/execute)
- `chown` - Changes file ownership

**Search Operations:**
- `grep` - Searches for text patterns inside files
- `find` - Searches for files and directories by name/properties

Which command would you like me to explain in detail?"""

        elif any(word in user_input for word in ['why', 'when', 'should i']):
            return """Excellent question! Understanding when to use each command is key:

**When to use ls:**
- Before doing anything - see what files are there
- After copying/moving - confirm it worked
- When looking for a specific file

**When to use cd:**
- Navigate to where your files are
- Go to project directories
- Return home with `cd ~`

**When to use chmod:**
- Make scripts executable: `chmod +x script.sh`
- Secure files: `chmod 600 private.txt` (only you can read/write)
- Share files: `chmod 644 document.txt` (others can read)

**When to use grep:**
- Find errors in log files: `grep "error" logfile.txt`
- Search code for functions: `grep "function" *.js`
- Filter command output: `ls | grep ".pdf"`

What situation are you trying to handle?"""

        # Linux command specific responses
        elif 'ls' in user_input:
            return """The **ls** command lists files and directories. Here's how it works:

**Basic Usage:**
- `ls` - Lists files in the current directory
- `ls -l` - Shows detailed information (permissions, size, date)
- `ls -a` - Shows all files including hidden ones (starting with .)
- `ls -la` - Combines both options for detailed view of all files

**Examples:**
- `ls Documents/` - Lists contents of Documents folder
- `ls -lh` - Shows file sizes in human-readable format (KB, MB, GB)
- `ls *.txt` - Lists only .txt files

The ls command is one of the most frequently used Linux commands for file management."""

        elif 'cd' in user_input:
            return """The **cd** command changes your current directory. Here's how to use it:

**Basic Usage:**
- `cd /path/to/directory` - Go to specific directory
- `cd ..` - Go up one directory level
- `cd ~` - Go to your home directory
- `cd -` - Go back to previous directory
- `cd` (alone) - Also goes to home directory

**Examples:**
- `cd /usr/local/bin` - Navigate to that specific path
- `cd ../Downloads` - Go up one level, then into Downloads
- `cd ~/Documents` - Go to Documents in your home folder

**Tip:** Use `pwd` after `cd` to see where you are now!"""

        elif 'pwd' in user_input:
            return """The **pwd** command shows your current directory location:

**Usage:**
- `pwd` - Prints the full path of where you are right now

**Example Output:**
If you're in your Documents folder, `pwd` might show:
`/home/username/Documents`

**Why it's useful:**
- Helps you know exactly where you are in the file system
- Useful when writing scripts that need to know the current location
- Great for confirming you're in the right place before running commands

PWD stands for "Print Working Directory"."""

        elif any(cmd in user_input for cmd in ['cat', 'file content', 'read file']):
            return """The **cat** command displays file contents:

**Basic Usage:**
- `cat filename.txt` - Shows the entire file content
- `cat file1.txt file2.txt` - Shows multiple files in sequence
- `cat -n filename.txt` - Shows content with line numbers

**Examples:**
- `cat /etc/hosts` - View system hosts file
- `cat script.sh` - View a shell script
- `cat log.txt | grep error` - Combine with grep to find errors

**Related commands:**
- `less filename.txt` - View large files page by page
- `head filename.txt` - Show just the first few lines
- `tail filename.txt` - Show just the last few lines"""

        elif any(word in user_input for word in ['cp', 'copy']):
            return """The **cp** command copies files and directories:

**Basic Usage:**
- `cp source destination` - Copy a file
- `cp -r folder/ backup/` - Copy directory recursively
- `cp -i file.txt backup.txt` - Copy with confirmation prompt

**Examples:**
- `cp document.txt backup.txt` - Copy file with new name
- `cp *.jpg /backup/images/` - Copy all JPG files to backup
- `cp -r project/ project-backup/` - Copy entire project folder

**Useful options:**
- `-r` or `-R` - Copy directories recursively
- `-i` - Ask before overwriting files
- `-v` - Verbose (show what's being copied)"""

        elif any(word in user_input for word in ['mv', 'move', 'rename']):
            return """The **mv** command moves/renames files and directories:

**Basic Usage:**
- `mv oldname newname` - Rename a file or folder
- `mv file.txt /new/location/` - Move file to different directory
- `mv *.txt documents/` - Move all .txt files to documents folder

**Examples:**
- `mv report.doc final_report.doc` - Rename file
- `mv temp_files/ archive/` - Move entire directory
- `mv file.txt backup/file_backup.txt` - Move AND rename

**Important:** Unlike `cp`, `mv` actually moves the file (removes from original location). Be careful not to overwrite important files!"""

        elif any(word in user_input for word in ['chmod', 'permission', 'access']):
            return """The **chmod** command changes file permissions:

**Basic Usage:**
- `chmod 755 script.sh` - Make file executable by owner, readable by others
- `chmod +x program` - Add execute permission
- `chmod -w file.txt` - Remove write permission

**Permission Numbers:**
- 7 = read + write + execute (rwx)
- 6 = read + write (rw-)
- 5 = read + execute (r-x)
- 4 = read only (r--)

**Examples:**
- `chmod 644 document.txt` - Owner can read/write, others can read
- `chmod +x script.sh` - Make script executable
- `chmod -R 755 website/` - Set permissions for entire directory"""

        elif any(word in user_input for word in ['chown', 'owner', 'ownership']):
            return """The **chown** command changes file ownership:

**Basic Usage:**
- `chown username file.txt` - Change owner of file
- `chown username:groupname file.txt` - Change owner and group
- `chown -R username folder/` - Change ownership recursively

**Examples:**
- `chown alice document.txt` - Make alice the owner
- `chown bob:developers script.sh` - Set bob as owner, developers as group
- `sudo chown root:root /system/file` - Change to root ownership (requires sudo)

**Note:** You usually need sudo (administrator privileges) to change ownership of files you don't own."""

        elif any(word in user_input for word in ['grep', 'search', 'find text']):
            return """The **grep** command searches for text patterns in files:

**Basic Usage:**
- `grep "pattern" file.txt` - Search for pattern in file
- `grep -r "pattern" directory/` - Search recursively in directory
- `grep -i "pattern" file.txt` - Case-insensitive search

**Examples:**
- `grep "error" log.txt` - Find lines containing "error"
- `grep -n "function" script.py` - Show line numbers with matches
- `ls | grep ".txt"` - Filter ls output to show only .txt files

**Useful options:**
- `-i` - Ignore case
- `-n` - Show line numbers
- `-v` - Show lines that DON'T match
- `-r` - Search recursively in directories"""

        elif any(word in user_input for word in ['find', 'locate', 'search files']):
            return """The **find** command searches for files and directories:

**Basic Usage:**
- `find . -name "filename"` - Find file by name in current directory
- `find /home -type f -name "*.txt"` - Find all .txt files in /home
- `find . -type d -name "project*"` - Find directories starting with "project"

**Examples:**
- `find . -name "*.py"` - Find all Python files
- `find /var/log -name "*.log" -mtime -7` - Find log files modified in last 7 days
- `find . -size +10M` - Find files larger than 10MB

**Search types:**
- `-type f` - Files only
- `-type d` - Directories only
- `-name` - Search by name (case sensitive)
- `-iname` - Search by name (case insensitive)"""

        # General Linux questions
        elif any(word in user_input for word in ['linux', 'commands', 'terminal', 'bash']):
            return """Linux commands are powerful tools for managing your system through the terminal. Here are the 10 essential commands you should know:

**File Operations:**
- `ls` - List files and directories
- `cd` - Change directory
- `pwd` - Show current directory
- `cat` - Display file contents
- `cp` - Copy files/directories
- `mv` - Move/rename files

**System Management:**
- `chmod` - Change file permissions
- `chown` - Change file ownership
- `grep` - Search text in files
- `find` - Search for files and directories

Each command has many options and can be combined with others. What specific command would you like to learn about?"""


        # Conversational responses
        elif any(word in user_input for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm here to help you learn Linux commands. You can ask me about any of the 10 essential commands: ls, cd, pwd, cat, cp, mv, chmod, chown, grep, and find. What would you like to learn about?"

        elif any(word in user_input for word in ['help', 'what can you do']):
            return """I can help you learn and understand Linux commands! Here's what I can do:

**Command Explanations:** I can explain how each Linux command works, with syntax and examples.

**Practical Examples:** I'll show you real-world usage scenarios for each command.

**Best Practices:** I can share tips and tricks for using commands effectively.

**Troubleshooting:** Help you understand error messages and common issues.

Try asking me about any of these commands: ls, cd, pwd, cat, cp, mv, chmod, chown, grep, find.

For example: "How does the ls command work?" or "What's the difference between cp and mv?"""

        # Common question patterns
        elif any(word in user_input for word in ['how do i', 'how to', 'how can i']):
            return """Great question! I can help you with Linux commands. Here are some common "how to" scenarios:

**File Operations:**
- "How do I list files?" → Use `ls` or `ls -la` for detailed view
- "How do I copy files?" → Use `cp source destination`  
- "How do I move files?" → Use `mv source destination`

**Navigation:**
- "How do I change directories?" → Use `cd /path/to/directory`
- "How do I see where I am?" → Use `pwd`

**File Content:**
- "How do I view file contents?" → Use `cat filename.txt`
- "How do I search in files?" → Use `grep "pattern" filename`

What specific task are you trying to accomplish?"""

        elif any(word in user_input for word in ['what is', 'what does', 'explain']):
            return """I can explain any of the Linux commands! Here's what each one does:

**File Listing & Navigation:**
- `ls` - Shows files and directories in current location
- `cd` - Changes your current directory
- `pwd` - Shows your current directory path

**File Operations:**
- `cat` - Displays file contents on screen  
- `cp` - Copies files or directories
- `mv` - Moves or renames files/directories

**Permissions & Ownership:**
- `chmod` - Changes file permissions (who can read/write/execute)
- `chown` - Changes file ownership

**Search Operations:**
- `grep` - Searches for text patterns inside files
- `find` - Searches for files and directories by name/properties

Which command would you like me to explain in detail?"""


        # Default intelligent response with more variety
        else:
            import random
            responses = [
                """I'm here to help you learn Linux! I can assist with any of these essential commands:

**File Management:** ls, cd, pwd, cat, cp, mv
**System Control:** chmod, chown, grep, find

Try asking me things like:
- "Show me ls examples"
- "How do I copy files?"
- "What's the difference between cp and mv?"

What would you like to explore?""",

                """Let me help you with Linux commands! I can explain, demonstrate, and provide examples for:

**Basic Commands:** ls (list), cd (change directory), pwd (current location)
**File Operations:** cat (view), cp (copy), mv (move/rename)  
**Advanced Tools:** chmod (permissions), chown (ownership), grep (search), find (locate)

What specific Linux task are you working on?""",

                """I'm your Linux command tutor! I can help you understand:

✓ Command syntax and options
✓ Real-world usage examples  
✓ Best practices and tips
✓ Common troubleshooting

The 10 essential commands I cover: ls, cd, pwd, cat, cp, mv, chmod, chown, grep, find

What aspect of Linux would you like to dive into?"""
            ]
            return random.choice(responses)

    def _get_general_response(self, user_input: str) -> str:
        """Generate general response for any topic"""
        
        # Greeting queries
        if any(word in user_input for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            return """Hello! It's great to meet you. I'm here to help with whatever you need - whether it's answering questions, helping with projects, having a conversation, or anything else you'd like assistance with. What's on your mind today?"""

        # Help or general queries
        elif any(word in user_input for word in ['help', 'what can you do', 'capabilities', 'assist']):
            return """I'm here to help with a wide variety of topics and tasks! I can:

**Answer Questions:** On virtually any subject - science, history, current events, academic topics, and more

**Help with Projects:** Writing, research, problem-solving, planning, creative projects

**Provide Explanations:** Break down complex topics, explain concepts, or help you understand something new

**Have Conversations:** Chat about your interests, thoughts, or anything you'd like to discuss

**Offer Advice:** Personal decisions, career guidance, learning strategies, or general life questions

**Creative Assistance:** Brainstorming, writing help, creative projects, or artistic endeavors

What would you like to explore or work on together?"""

        # Technical topics (but not restricted to them)
        elif any(word in user_input for word in ['programming', 'code', 'linux', 'computer', 'technology']):
            return """I'd be happy to help with technical topics! I can assist with programming, Linux commands, computer science concepts, web development, databases, and much more. 

But I'm not limited to technical subjects - I can help with any topic you're interested in. What specific area would you like to explore or what questions do you have?"""

        # General fallback for any other topic
        else:
            return """I'm here to help with whatever you'd like to discuss or work on! Whether it's:

- Answering questions on any topic
- Helping with projects or assignments  
- Having a thoughtful conversation
- Providing explanations or advice
- Creative brainstorming
- Problem-solving assistance

Feel free to ask me about anything - from everyday questions to complex topics, personal matters, academic subjects, creative projects, or just casual conversation. What's on your mind?"""

    def _get_linux_command_help(self, user_input: str) -> str:
        """Provide help for specific Linux commands"""
        
        if 'ls' in user_input:
            return """**ls - List Directory Contents**
**Purpose**: Display files and directories
**Basic Syntax**: `ls [options] [directory]`
**Examples**:
- `ls` - List current directory contents
- `ls -l` - Detailed list with permissions and sizes
- `ls -a` - Show all files including hidden ones
- `ls /home/user` - List contents of specific directory
**Tip**: Use `ls -la` to see everything in detail!"""
        
        elif 'cd' in user_input:
            return """**cd - Change Directory**
**Purpose**: Navigate between directories
**Basic Syntax**: `cd [directory]`
**Examples**:
- `cd /home/user` - Go to specific path
- `cd ..` - Go up one directory
- `cd ~` - Go to home directory
- `cd -` - Go back to previous directory
**Tip**: Use `pwd` after `cd` to confirm your location!"""
        
        elif 'pwd' in user_input:
            return """**pwd - Print Working Directory**
**Purpose**: Show your current location in the file system
**Basic Syntax**: `pwd`
**Example**: Simply type `pwd` and it shows your current path
**Tip**: Useful for orientation when navigating directories!"""
        
        else:
            return """I can help with various Linux commands! Here are some common ones:

**File and Directory Commands:**
- `cat` - Display file contents
- `grep` - Search text within files  
- `find` - Search for files and directories
- `chmod` - Change file permissions
- `ssh` - Secure shell for remote access
- `ps` - Show running processes
- `top` - Display running processes (live)

Ask me about any specific command and I'll explain how to use it!"""
    
    def get_or_create_chat_session(self, study_session):
        """Get or create chat session for study session"""
        try:
            logger.info(f"Attempting to get or create chat session for study session: {study_session.session_id}")
            logger.info(f"User: {study_session.user}, User ID: {study_session.user.id}")
            
            chat_session, created = ChatSession.objects.get_or_create(
                session=study_session,
                defaults={
                    'user': study_session.user
                }
            )
            
            logger.info(f"Chat session {'created' if created else 'retrieved'}: {chat_session.id}")
            return chat_session, created
        except Exception as e:
            logger.error(f"Error creating chat session: {str(e)}")
            logger.error(f"Study session: {study_session}")
            logger.error(f"User: {study_session.user}")
            raise
