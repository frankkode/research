import { Question } from '../types';

// Immediate Recall Quiz Questions (10 questions - test direct recall of studied material)
export const immediateRecallQuestions: Question[] = [
  {
    id: 'ir-1',
    question_text: 'Which command is used to list files and directories in the current directory?',
    question_type: 'multiple_choice',
    order: 1,
    is_required: true,
    category: 'basic_commands',
    difficulty: 'easy',
    correct_answer_id: 'ir-1-a',
    choices: [
      { id: 'ir-1-a', choice_text: 'ls', order: 1, is_correct: true },
      { id: 'ir-1-b', choice_text: 'cd', order: 2, is_correct: false },
      { id: 'ir-1-c', choice_text: 'pwd', order: 3, is_correct: false },
      { id: 'ir-1-d', choice_text: 'cat', order: 4, is_correct: false }
    ]
  },
  {
    id: 'ir-2',
    question_text: 'What does the "pwd" command do?',
    question_type: 'multiple_choice',
    order: 2,
    is_required: true,
    category: 'basic_commands',
    difficulty: 'easy',
    correct_answer_id: 'ir-2-b',
    choices: [
      { id: 'ir-2-a', choice_text: 'Lists directory contents', order: 1, is_correct: false },
      { id: 'ir-2-b', choice_text: 'Shows current working directory', order: 2, is_correct: true },
      { id: 'ir-2-c', choice_text: 'Changes directory', order: 3, is_correct: false },
      { id: 'ir-2-d', choice_text: 'Creates a new directory', order: 4, is_correct: false }
    ]
  },
  {
    id: 'ir-3',
    question_text: 'Which command is used to change to a different directory?',
    question_type: 'multiple_choice',
    order: 3,
    is_required: true,
    category: 'basic_commands',
    difficulty: 'easy',
    correct_answer_id: 'ir-3-c',
    choices: [
      { id: 'ir-3-a', choice_text: 'ls', order: 1, is_correct: false },
      { id: 'ir-3-b', choice_text: 'pwd', order: 2, is_correct: false },
      { id: 'ir-3-c', choice_text: 'cd', order: 3, is_correct: true },
      { id: 'ir-3-d', choice_text: 'mv', order: 4, is_correct: false }
    ]
  },
  {
    id: 'ir-4',
    question_text: 'What is the purpose of the "cat" command?',
    question_type: 'multiple_choice',
    order: 4,
    is_required: true,
    category: 'file_operations',
    difficulty: 'easy',
    correct_answer_id: 'ir-4-a',
    choices: [
      { id: 'ir-4-a', choice_text: 'Display file contents', order: 1, is_correct: true },
      { id: 'ir-4-b', choice_text: 'Copy files', order: 2, is_correct: false },
      { id: 'ir-4-c', choice_text: 'Move files', order: 3, is_correct: false },
      { id: 'ir-4-d', choice_text: 'Delete files', order: 4, is_correct: false }
    ]
  },
  {
    id: 'ir-5',
    question_text: 'Which command is used to copy files or directories?',
    question_type: 'multiple_choice',
    order: 5,
    is_required: true,
    category: 'file_operations',
    difficulty: 'easy',
    correct_answer_id: 'ir-5-b',
    choices: [
      { id: 'ir-5-a', choice_text: 'mv', order: 1, is_correct: false },
      { id: 'ir-5-b', choice_text: 'cp', order: 2, is_correct: true },
      { id: 'ir-5-c', choice_text: 'cat', order: 3, is_correct: false },
      { id: 'ir-5-d', choice_text: 'ls', order: 4, is_correct: false }
    ]
  },
  {
    id: 'ir-6',
    question_text: 'What does the "mv" command do?',
    question_type: 'multiple_choice',
    order: 6,
    is_required: true,
    category: 'file_operations',
    difficulty: 'easy',
    correct_answer_id: 'ir-6-c',
    choices: [
      { id: 'ir-6-a', choice_text: 'Copy files', order: 1, is_correct: false },
      { id: 'ir-6-b', choice_text: 'Display file contents', order: 2, is_correct: false },
      { id: 'ir-6-c', choice_text: 'Move or rename files', order: 3, is_correct: true },
      { id: 'ir-6-d', choice_text: 'Delete files', order: 4, is_correct: false }
    ]
  },
  {
    id: 'ir-7',
    question_text: 'Which command is used to change file permissions?',
    question_type: 'multiple_choice',
    order: 7,
    is_required: true,
    category: 'permissions',
    difficulty: 'medium',
    correct_answer_id: 'ir-7-a',
    choices: [
      { id: 'ir-7-a', choice_text: 'chmod', order: 1, is_correct: true },
      { id: 'ir-7-b', choice_text: 'chown', order: 2, is_correct: false },
      { id: 'ir-7-c', choice_text: 'cp', order: 3, is_correct: false },
      { id: 'ir-7-d', choice_text: 'mv', order: 4, is_correct: false }
    ]
  },
  {
    id: 'ir-8',
    question_text: 'What is the purpose of the "chown" command?',
    question_type: 'multiple_choice',
    order: 8,
    is_required: true,
    category: 'permissions',
    difficulty: 'medium',
    correct_answer_id: 'ir-8-b',
    choices: [
      { id: 'ir-8-a', choice_text: 'Change file permissions', order: 1, is_correct: false },
      { id: 'ir-8-b', choice_text: 'Change file ownership', order: 2, is_correct: true },
      { id: 'ir-8-c', choice_text: 'Change directory', order: 3, is_correct: false },
      { id: 'ir-8-d', choice_text: 'Change file name', order: 4, is_correct: false }
    ]
  },
  {
    id: 'ir-9',
    question_text: 'Which command is used to search for text patterns in files?',
    question_type: 'multiple_choice',
    order: 9,
    is_required: true,
    category: 'search',
    difficulty: 'medium',
    correct_answer_id: 'ir-9-c',
    choices: [
      { id: 'ir-9-a', choice_text: 'find', order: 1, is_correct: false },
      { id: 'ir-9-b', choice_text: 'ls', order: 2, is_correct: false },
      { id: 'ir-9-c', choice_text: 'grep', order: 3, is_correct: true },
      { id: 'ir-9-d', choice_text: 'cat', order: 4, is_correct: false }
    ]
  },
  {
    id: 'ir-10',
    question_text: 'What does the "find" command do?',
    question_type: 'multiple_choice',
    order: 10,
    is_required: true,
    category: 'search',
    difficulty: 'medium',
    correct_answer_id: 'ir-10-a',
    choices: [
      { id: 'ir-10-a', choice_text: 'Search for files and directories', order: 1, is_correct: true },
      { id: 'ir-10-b', choice_text: 'Search for text in files', order: 2, is_correct: false },
      { id: 'ir-10-c', choice_text: 'Display file contents', order: 3, is_correct: false },
      { id: 'ir-10-d', choice_text: 'List directory contents', order: 4, is_correct: false }
    ]
  }
];

// Transfer Quiz Questions (5 questions - test application of knowledge to new scenarios)
export const transferQuestions: Question[] = [
  {
    id: 'tf-1',
    question_text: 'You want to create a backup of a file called "report.txt" in the same directory. Which command would you use?',
    question_type: 'multiple_choice',
    order: 1,
    is_required: true,
    category: 'file_operations',
    difficulty: 'medium',
    correct_answer_id: 'tf-1-b',
    choices: [
      { id: 'tf-1-a', choice_text: 'mv report.txt backup.txt', order: 1, is_correct: false },
      { id: 'tf-1-b', choice_text: 'cp report.txt report_backup.txt', order: 2, is_correct: true },
      { id: 'tf-1-c', choice_text: 'cat report.txt > backup.txt', order: 3, is_correct: false },
      { id: 'tf-1-d', choice_text: 'ls report.txt backup.txt', order: 4, is_correct: false }
    ]
  },
  {
    id: 'tf-2',
    question_text: 'You are in the /home/user directory and want to navigate to /home/user/documents/projects. Which command is correct?',
    question_type: 'multiple_choice',
    order: 2,
    is_required: true,
    category: 'navigation',
    difficulty: 'medium',
    correct_answer_id: 'tf-2-c',
    choices: [
      { id: 'tf-2-a', choice_text: 'cd /documents/projects', order: 1, is_correct: false },
      { id: 'tf-2-b', choice_text: 'cd ../documents/projects', order: 2, is_correct: false },
      { id: 'tf-2-c', choice_text: 'cd documents/projects', order: 3, is_correct: true },
      { id: 'tf-2-d', choice_text: 'pwd documents/projects', order: 4, is_correct: false }
    ]
  },
  {
    id: 'tf-3',
    question_text: 'You need to find all files with ".log" extension in the current directory and subdirectories. Which command would you use?',
    question_type: 'multiple_choice',
    order: 3,
    is_required: true,
    category: 'search',
    difficulty: 'hard',
    correct_answer_id: 'tf-3-a',
    choices: [
      { id: 'tf-3-a', choice_text: 'find . -name "*.log"', order: 1, is_correct: true },
      { id: 'tf-3-b', choice_text: 'grep "*.log" .', order: 2, is_correct: false },
      { id: 'tf-3-c', choice_text: 'ls *.log', order: 3, is_correct: false },
      { id: 'tf-3-d', choice_text: 'cat *.log', order: 4, is_correct: false }
    ]
  },
  {
    id: 'tf-4',
    question_text: 'You want to make a script file executable for everyone. Which command would you use?',
    question_type: 'multiple_choice',
    order: 4,
    is_required: true,
    category: 'permissions',
    difficulty: 'hard',
    correct_answer_id: 'tf-4-b',
    choices: [
      { id: 'tf-4-a', choice_text: 'chown +x script.sh', order: 1, is_correct: false },
      { id: 'tf-4-b', choice_text: 'chmod +x script.sh', order: 2, is_correct: true },
      { id: 'tf-4-c', choice_text: 'mv +x script.sh', order: 3, is_correct: false },
      { id: 'tf-4-d', choice_text: 'cp +x script.sh', order: 4, is_correct: false }
    ]
  },
  {
    id: 'tf-5',
    question_text: 'You want to search for the word "error" in all files in the current directory. Which command would you use?',
    question_type: 'multiple_choice',
    order: 5,
    is_required: true,
    category: 'search',
    difficulty: 'hard',
    correct_answer_id: 'tf-5-c',
    choices: [
      { id: 'tf-5-a', choice_text: 'find . -name "error"', order: 1, is_correct: false },
      { id: 'tf-5-b', choice_text: 'ls error *', order: 2, is_correct: false },
      { id: 'tf-5-c', choice_text: 'grep "error" *', order: 3, is_correct: true },
      { id: 'tf-5-d', choice_text: 'cat error *', order: 4, is_correct: false }
    ]
  }
];

// Pre-assessment Questions (10 questions- test prior knowledge)
export const preAssessmentQuestions: Question[] = [
  {
    id: 'pre-1',
    question_text: 'Have you used Linux command line before?',
    question_type: 'multiple_choice',
    order: 1,
    is_required: true,
    category: 'background',
    difficulty: 'easy',
    correct_answer_id: 'pre-1-a', // No correct answer for survey questions
    choices: [
      { id: 'pre-1-a', choice_text: 'Never', order: 1, is_correct: false },
      { id: 'pre-1-b', choice_text: 'Rarely (a few times)', order: 2, is_correct: false },
      { id: 'pre-1-c', choice_text: 'Sometimes (monthly)', order: 3, is_correct: false },
      { id: 'pre-1-d', choice_text: 'Frequently (weekly or daily)', order: 4, is_correct: false }
    ]
  },
  {
    id: 'pre-2',
    question_text: 'Which command lists files in a directory?',
    question_type: 'multiple_choice',
    order: 2,
    is_required: true,
    category: 'basic_commands',
    difficulty: 'easy',
    correct_answer_id: 'pre-2-a',
    choices: [
      { id: 'pre-2-a', choice_text: 'ls', order: 1, is_correct: true },
      { id: 'pre-2-b', choice_text: 'dir', order: 2, is_correct: false },
      { id: 'pre-2-c', choice_text: 'list', order: 3, is_correct: false },
      { id: 'pre-2-d', choice_text: 'show', order: 4, is_correct: false }
    ]
  },
  {
    id: 'pre-3',
    question_text: 'What does "cd" stand for?',
    question_type: 'multiple_choice',
    order: 3,
    is_required: true,
    category: 'basic_commands',
    difficulty: 'easy',
    correct_answer_id: 'pre-3-b',
    choices: [
      { id: 'pre-3-a', choice_text: 'Copy directory', order: 1, is_correct: false },
      { id: 'pre-3-b', choice_text: 'Change directory', order: 2, is_correct: true },
      { id: 'pre-3-c', choice_text: 'Create directory', order: 3, is_correct: false },
      { id: 'pre-3-d', choice_text: 'Current directory', order: 4, is_correct: false }
    ]
  },
  {
    id: 'pre-4',
    question_text: 'Which command shows your current location in the file system?',
    question_type: 'multiple_choice',
    order: 4,
    is_required: true,
    category: 'basic_commands',
    difficulty: 'easy',
    correct_answer_id: 'pre-4-c',
    choices: [
      { id: 'pre-4-a', choice_text: 'where', order: 1, is_correct: false },
      { id: 'pre-4-b', choice_text: 'location', order: 2, is_correct: false },
      { id: 'pre-4-c', choice_text: 'pwd', order: 3, is_correct: true },
      { id: 'pre-4-d', choice_text: 'current', order: 4, is_correct: false }
    ]
  },
  {
    id: 'pre-5',
    question_text: 'Which command is used to copy files?',
    question_type: 'multiple_choice',
    order: 5,
    is_required: true,
    category: 'file_operations',
    difficulty: 'medium',
    correct_answer_id: 'pre-5-b',
    choices: [
      { id: 'pre-5-a', choice_text: 'copy', order: 1, is_correct: false },
      { id: 'pre-5-b', choice_text: 'cp', order: 2, is_correct: true },
      { id: 'pre-5-c', choice_text: 'mv', order: 3, is_correct: false },
      { id: 'pre-5-d', choice_text: 'duplicate', order: 4, is_correct: false }
    ]
  },
  {
    id: 'pre-6',
    question_text: 'What does the "mv" command do?',
    question_type: 'multiple_choice',
    order: 6,
    is_required: true,
    category: 'file_operations',
    difficulty: 'medium',
    correct_answer_id: 'pre-6-a',
    choices: [
      { id: 'pre-6-a', choice_text: 'Move or rename files', order: 1, is_correct: true },
      { id: 'pre-6-b', choice_text: 'Make directory', order: 2, is_correct: false },
      { id: 'pre-6-c', choice_text: 'Multiple view', order: 3, is_correct: false },
      { id: 'pre-6-d', choice_text: 'Merge files', order: 4, is_correct: false }
    ]
  },
  {
    id: 'pre-7',
    question_text: 'Which command changes file permissions?',
    question_type: 'multiple_choice',
    order: 7,
    is_required: true,
    category: 'permissions',
    difficulty: 'medium',
    correct_answer_id: 'pre-7-c',
    choices: [
      { id: 'pre-7-a', choice_text: 'perm', order: 1, is_correct: false },
      { id: 'pre-7-b', choice_text: 'access', order: 2, is_correct: false },
      { id: 'pre-7-c', choice_text: 'chmod', order: 3, is_correct: true },
      { id: 'pre-7-d', choice_text: 'rights', order: 4, is_correct: false }
    ]
  },
  {
    id: 'pre-8',
    question_text: 'What is the purpose of the "grep" command?',
    question_type: 'multiple_choice',
    order: 8,
    is_required: true,
    category: 'search',
    difficulty: 'medium',
    correct_answer_id: 'pre-8-b',
    choices: [
      { id: 'pre-8-a', choice_text: 'Get files', order: 1, is_correct: false },
      { id: 'pre-8-b', choice_text: 'Search for text patterns', order: 2, is_correct: true },
      { id: 'pre-8-c', choice_text: 'Group files', order: 3, is_correct: false },
      { id: 'pre-8-d', choice_text: 'Generate report', order: 4, is_correct: false }
    ]
  },
  {
    id: 'pre-9',
    question_text: 'Which command finds files and directories?',
    question_type: 'multiple_choice',
    order: 9,
    is_required: true,
    category: 'search',
    difficulty: 'medium',
    correct_answer_id: 'pre-9-d',
    choices: [
      { id: 'pre-9-a', choice_text: 'search', order: 1, is_correct: false },
      { id: 'pre-9-b', choice_text: 'locate', order: 2, is_correct: false },
      { id: 'pre-9-c', choice_text: 'get', order: 3, is_correct: false },
      { id: 'pre-9-d', choice_text: 'find', order: 4, is_correct: true }
    ]
  },
  {
    id: 'pre-10',
    question_text: 'How comfortable are you with using command line interfaces?',
    question_type: 'multiple_choice',
    order: 10,
    is_required: true,
    category: 'background',
    difficulty: 'easy',
    correct_answer_id: 'pre-10-a', // No correct answer for survey questions
    choices: [
      { id: 'pre-10-a', choice_text: 'Very uncomfortable', order: 1, is_correct: false },
      { id: 'pre-10-b', choice_text: 'Somewhat uncomfortable', order: 2, is_correct: false },
      { id: 'pre-10-c', choice_text: 'Neutral', order: 3, is_correct: false },
      { id: 'pre-10-d', choice_text: 'Somewhat comfortable', order: 4, is_correct: false },
      { id: 'pre-10-e', choice_text: 'Very comfortable', order: 5, is_correct: false }
    ]
  }
];

export const getQuizQuestions = (quizType: 'immediate_recall' | 'transfer' | 'pre_assessment'): Question[] => {
  switch (quizType) {
    case 'immediate_recall':
      return immediateRecallQuestions;
    case 'transfer':
      return transferQuestions;
    case 'pre_assessment':
      return preAssessmentQuestions;
    default:
      return [];
  }
};