#!/usr/bin/env python3
"""
Learning Effectiveness Analysis and Visualization
Comprehensive analysis of ChatGPT vs PDF learning methods
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.patches import Patch
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def create_sample_data():
    """Create sample data based on the provided metrics"""
    
    # Learning Effectiveness Metrics
    learning_metrics = {
        'Method': ['ChatGPT', 'PDF'],
        'Learning_Gain': [85.2, 72.8],
        'Time_Efficiency_Minutes': [45, 68],
        'Completion_Rate': [92.5, 78.3],
        'Pre_Quiz_Score': [42.1, 41.8],
        'Post_Quiz_Score': [87.3, 74.6]
    }
    
    # Question-level performance data
    questions_data = {
        'Question_ID': [f'Q{i}' for i in range(1, 21)],
        'Difficulty': np.random.choice(['Easy', 'Medium', 'Hard'], 20, p=[0.3, 0.5, 0.2]),
        'Question_Type': np.random.choice(['Conceptual', 'Applied', 'Analysis'], 20, p=[0.4, 0.4, 0.2]),
        'ChatGPT_Accuracy': np.random.uniform(0.7, 0.95, 20),
        'PDF_Accuracy': np.random.uniform(0.6, 0.85, 20),
        'ChatGPT_Improvement': np.random.uniform(0.3, 0.6, 20),
        'PDF_Improvement': np.random.uniform(0.2, 0.5, 20)
    }
    
    return pd.DataFrame(learning_metrics), pd.DataFrame(questions_data)

def plot_learning_effectiveness_overview(df_metrics):
    """Create comprehensive overview of learning effectiveness"""
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Learning Effectiveness Analysis: ChatGPT vs PDF Methods', fontsize=16, fontweight='bold')
    
    # 1. Learning Gain Comparison
    ax1 = axes[0, 0]
    bars1 = ax1.bar(df_metrics['Method'], df_metrics['Learning_Gain'], 
                    color=['#FF6B6B', '#4ECDC4'], alpha=0.8)
    ax1.set_title('Learning Gain Comparison', fontweight='bold')
    ax1.set_ylabel('Learning Gain (%)')
    ax1.set_ylim(0, 100)
    for i, v in enumerate(df_metrics['Learning_Gain']):
        ax1.text(i, v + 2, f'{v}%', ha='center', fontweight='bold')
    
    # 2. Time Efficiency
    ax2 = axes[0, 1]
    bars2 = ax2.bar(df_metrics['Method'], df_metrics['Time_Efficiency_Minutes'], 
                    color=['#FFE66D', '#FF6B9D'], alpha=0.8)
    ax2.set_title('Time Efficiency', fontweight='bold')
    ax2.set_ylabel('Time (Minutes)')
    ax2.invert_yaxis()  # Lower is better
    for i, v in enumerate(df_metrics['Time_Efficiency_Minutes']):
        ax2.text(i, v - 3, f'{v}min', ha='center', fontweight='bold')
    
    # 3. Completion Rates
    ax3 = axes[0, 2]
    bars3 = ax3.bar(df_metrics['Method'], df_metrics['Completion_Rate'], 
                    color=['#95E1D3', '#F38BA8'], alpha=0.8)
    ax3.set_title('Completion Rates', fontweight='bold')
    ax3.set_ylabel('Completion Rate (%)')
    ax3.set_ylim(0, 100)
    for i, v in enumerate(df_metrics['Completion_Rate']):
        ax3.text(i, v + 2, f'{v}%', ha='center', fontweight='bold')
    
    # 4. Pre vs Post Quiz Scores
    ax4 = axes[1, 0]
    x = np.arange(len(df_metrics['Method']))
    width = 0.35
    ax4.bar(x - width/2, df_metrics['Pre_Quiz_Score'], width, label='Pre-Quiz', alpha=0.8)
    ax4.bar(x + width/2, df_metrics['Post_Quiz_Score'], width, label='Post-Quiz', alpha=0.8)
    ax4.set_title('Pre vs Post Quiz Score Comparison', fontweight='bold')
    ax4.set_ylabel('Quiz Score (%)')
    ax4.set_xticks(x)
    ax4.set_xticklabels(df_metrics['Method'])
    ax4.legend()
    ax4.set_ylim(0, 100)
    
    # 5. Improvement Calculation
    ax5 = axes[1, 1]
    improvement = df_metrics['Post_Quiz_Score'] - df_metrics['Pre_Quiz_Score']
    bars5 = ax5.bar(df_metrics['Method'], improvement, 
                    color=['#A8E6CF', '#DCEDC1'], alpha=0.8)
    ax5.set_title('Score Improvement', fontweight='bold')
    ax5.set_ylabel('Improvement (Points)')
    for i, v in enumerate(improvement):
        ax5.text(i, v + 1, f'+{v:.1f}', ha='center', fontweight='bold')
    
    # 6. Overall Effectiveness Score
    ax6 = axes[1, 2]
    # Composite score: weighted average of normalized metrics
    effectiveness_score = []
    for i in range(len(df_metrics)):
        score = (df_metrics['Learning_Gain'][i] * 0.3 + 
                df_metrics['Completion_Rate'][i] * 0.2 + 
                (100 - df_metrics['Time_Efficiency_Minutes'][i]/max(df_metrics['Time_Efficiency_Minutes']) * 100) * 0.2 +
                improvement[i] * 0.3)
        effectiveness_score.append(score)
    
    bars6 = ax6.bar(df_metrics['Method'], effectiveness_score, 
                    color=['#B4A7D6', '#D4A574'], alpha=0.8)
    ax6.set_title('Overall Effectiveness Score', fontweight='bold')
    ax6.set_ylabel('Composite Score')
    for i, v in enumerate(effectiveness_score):
        ax6.text(i, v + 2, f'{v:.1f}', ha='center', fontweight='bold')
    
    plt.tight_layout()
    return fig

def plot_question_level_analysis(df_questions):
    """Analyze question-level performance"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Question-Level Performance Analysis', fontsize=16, fontweight='bold')
    
    # 1. Accuracy by Question Type
    ax1 = axes[0, 0]
    accuracy_by_type = df_questions.groupby('Question_Type')[['ChatGPT_Accuracy', 'PDF_Accuracy']].mean()
    accuracy_by_type.plot(kind='bar', ax=ax1, alpha=0.8)
    ax1.set_title('Accuracy by Question Type', fontweight='bold')
    ax1.set_ylabel('Accuracy (%)')
    ax1.legend(['ChatGPT', 'PDF'])
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Accuracy by Difficulty Level
    ax2 = axes[0, 1]
    accuracy_by_difficulty = df_questions.groupby('Difficulty')[['ChatGPT_Accuracy', 'PDF_Accuracy']].mean()
    accuracy_by_difficulty.plot(kind='bar', ax=ax2, alpha=0.8)
    ax2.set_title('Accuracy by Question Difficulty', fontweight='bold')
    ax2.set_ylabel('Accuracy (%)')
    ax2.legend(['ChatGPT', 'PDF'])
    ax2.tick_params(axis='x', rotation=45)
    
    # 3. Improvement Comparison
    ax3 = axes[1, 0]
    improvement_by_type = df_questions.groupby('Question_Type')[['ChatGPT_Improvement', 'PDF_Improvement']].mean()
    improvement_by_type.plot(kind='bar', ax=ax3, alpha=0.8)
    ax3.set_title('Learning Improvement by Question Type', fontweight='bold')
    ax3.set_ylabel('Improvement (%)')
    ax3.legend(['ChatGPT', 'PDF'])
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. Better Method Analysis
    ax4 = axes[1, 1]
    df_questions['Better_Method'] = np.where(
        df_questions['ChatGPT_Accuracy'] > df_questions['PDF_Accuracy'], 
        'ChatGPT', 'PDF'
    )
    better_method_counts = df_questions['Better_Method'].value_counts()
    colors = ['#FF6B6B' if method == 'ChatGPT' else '#4ECDC4' for method in better_method_counts.index]
    wedges, texts, autotexts = ax4.pie(better_method_counts.values, labels=better_method_counts.index, 
                                      autopct='%1.1f%%', colors=colors)
    ax4.set_title('Better Performing Method Distribution', fontweight='bold')
    
    plt.tight_layout()
    return fig

def plot_detailed_comparison(df_questions):
    """Create detailed comparison visualizations"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Detailed Performance Comparison', fontsize=16, fontweight='bold')
    
    # 1. Scatter plot: ChatGPT vs PDF Accuracy
    ax1 = axes[0, 0]
    scatter = ax1.scatter(df_questions['PDF_Accuracy'], df_questions['ChatGPT_Accuracy'], 
                         c=df_questions['Difficulty'].map({'Easy': 0, 'Medium': 1, 'Hard': 2}),
                         cmap='viridis', alpha=0.7, s=100)
    ax1.plot([0, 1], [0, 1], 'r--', alpha=0.8)  # Diagonal line
    ax1.set_xlabel('PDF Accuracy')
    ax1.set_ylabel('ChatGPT Accuracy')
    ax1.set_title('Accuracy Correlation: ChatGPT vs PDF')
    
    # Add colorbar for difficulty
    cbar = plt.colorbar(scatter, ax=ax1)
    cbar.set_ticks([0, 1, 2])
    cbar.set_ticklabels(['Easy', 'Medium', 'Hard'])
    cbar.set_label('Question Difficulty')
    
    # 2. Box plot: Accuracy distribution by method
    ax2 = axes[0, 1]
    accuracy_data = [df_questions['ChatGPT_Accuracy'], df_questions['PDF_Accuracy']]
    box_plot = ax2.boxplot(accuracy_data, labels=['ChatGPT', 'PDF'], patch_artist=True)
    colors = ['#FF6B6B', '#4ECDC4']
    for patch, color in zip(box_plot['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax2.set_title('Accuracy Distribution by Method')
    ax2.set_ylabel('Accuracy')
    
    # 3. Heatmap: Performance by Type and Difficulty
    ax3 = axes[1, 0]
    pivot_chatgpt = df_questions.pivot_table(values='ChatGPT_Accuracy', 
                                            index='Question_Type', 
                                            columns='Difficulty', 
                                            aggfunc='mean')
    sns.heatmap(pivot_chatgpt, annot=True, cmap='Reds', ax=ax3, fmt='.2f')
    ax3.set_title('ChatGPT Accuracy Heatmap')
    
    # 4. Heatmap: PDF Performance
    ax4 = axes[1, 1]
    pivot_pdf = df_questions.pivot_table(values='PDF_Accuracy', 
                                        index='Question_Type', 
                                        columns='Difficulty', 
                                        aggfunc='mean')
    sns.heatmap(pivot_pdf, annot=True, cmap='Blues', ax=ax4, fmt='.2f')
    ax4.set_title('PDF Accuracy Heatmap')
    
    plt.tight_layout()
    return fig

def generate_summary_statistics(df_metrics, df_questions):
    """Generate comprehensive summary statistics"""
    print("=" * 80)
    print("LEARNING EFFECTIVENESS ANALYSIS SUMMARY")
    print("=" * 80)
    
    print("\n📊 OVERALL PERFORMANCE METRICS")
    print("-" * 40)
    for i, method in enumerate(df_metrics['Method']):
        print(f"\n{method} Method:")
        print(f"  • Learning Gain: {df_metrics['Learning_Gain'][i]:.1f}%")
        print(f"  • Time Efficiency: {df_metrics['Time_Efficiency_Minutes'][i]} minutes")
        print(f"  • Completion Rate: {df_metrics['Completion_Rate'][i]:.1f}%")
        print(f"  • Score Improvement: {df_metrics['Post_Quiz_Score'][i] - df_metrics['Pre_Quiz_Score'][i]:.1f} points")
    
    print("\n🎯 QUESTION-LEVEL ANALYSIS")
    print("-" * 40)
    
    # Accuracy by difficulty
    print("\nAccuracy by Difficulty Level:")
    for difficulty in ['Easy', 'Medium', 'Hard']:
        subset = df_questions[df_questions['Difficulty'] == difficulty]
        if len(subset) > 0:
            chatgpt_acc = subset['ChatGPT_Accuracy'].mean()
            pdf_acc = subset['PDF_Accuracy'].mean()
            print(f"  {difficulty}: ChatGPT {chatgpt_acc:.1%}, PDF {pdf_acc:.1%}")
    
    # Best performing method
    chatgpt_wins = (df_questions['ChatGPT_Accuracy'] > df_questions['PDF_Accuracy']).sum()
    pdf_wins = (df_questions['PDF_Accuracy'] > df_questions['ChatGPT_Accuracy']).sum()
    ties = (df_questions['ChatGPT_Accuracy'] == df_questions['PDF_Accuracy']).sum()
    
    print(f"\n🏆 PERFORMANCE COMPARISON")
    print("-" * 40)
    print(f"Questions where ChatGPT performed better: {chatgpt_wins}")
    print(f"Questions where PDF performed better: {pdf_wins}")
    print(f"Ties: {ties}")
    
    print(f"\n📈 KEY INSIGHTS")
    print("-" * 40)
    
    # Calculate key insights
    learning_gain_advantage = df_metrics['Learning_Gain'][0] - df_metrics['Learning_Gain'][1]
    time_efficiency_advantage = df_metrics['Time_Efficiency_Minutes'][1] - df_metrics['Time_Efficiency_Minutes'][0]
    completion_advantage = df_metrics['Completion_Rate'][0] - df_metrics['Completion_Rate'][1]
    
    print(f"• ChatGPT shows {learning_gain_advantage:.1f}% higher learning gain")
    print(f"• ChatGPT is {time_efficiency_advantage} minutes faster on average")
    print(f"• ChatGPT has {completion_advantage:.1f}% higher completion rate")
    print(f"• Overall accuracy: ChatGPT {df_questions['ChatGPT_Accuracy'].mean():.1%}, PDF {df_questions['PDF_Accuracy'].mean():.1%}")

def main():
    """Main execution function"""
    print("Generating Learning Effectiveness Analysis...")
    
    # Create sample data
    df_metrics, df_questions = create_sample_data()
    
    # Generate visualizations
    fig1 = plot_learning_effectiveness_overview(df_metrics)
    fig2 = plot_question_level_analysis(df_questions)
    fig3 = plot_detailed_comparison(df_questions)
    
    # Save plots
    fig1.savefig('/Users/masabosimplicefrank/linux-learning-study/learning_effectiveness_overview.png', 
                 dpi=300, bbox_inches='tight')
    fig2.savefig('/Users/masabosimplicefrank/linux-learning-study/question_level_analysis.png', 
                 dpi=300, bbox_inches='tight')
    fig3.savefig('/Users/masabosimplicefrank/linux-learning-study/detailed_comparison.png', 
                 dpi=300, bbox_inches='tight')
    
    # Generate summary statistics
    generate_summary_statistics(df_metrics, df_questions)
    
    # Close plots to avoid display issues
    plt.close('all')
    
    print(f"\n✅ Analysis complete! Visualizations saved to:")
    print(f"   • learning_effectiveness_overview.png")
    print(f"   • question_level_analysis.png") 
    print(f"   • detailed_comparison.png")

if __name__ == "__main__":
    main()