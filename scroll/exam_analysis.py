import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter
import argparse

def analyze_student_performance(answer_key, student_answers_csv, low_performance_threshold=0.5):
    """
    Analyze student performance on multiple choice questions
    
    Parameters:
    answer_key (list): List of correct answers for each question
    student_answers_csv (str): Path to CSV file with student answers
    low_performance_threshold (float): Threshold for low performance questions (default: 0.5)
    """
    # Read student answers
    df = pd.read_csv(student_answers_csv)
    
    # Validate data
    if len(answer_key) != df.shape[1]:
        raise ValueError(f"Answer key has {len(answer_key)} questions but CSV has {df.shape[1]} columns")
    
    # Calculate performance metrics
    results = {}
    total_students = len(df)
    
    for i, correct_answer in enumerate(answer_key):
        question_num = i + 1
        question_col = df.iloc[:, i]
        
        # Calculate correct rate
        correct_count = (question_col == correct_answer).sum()
        correct_rate = correct_count / total_students
        
        # Get wrong answers
        wrong_answers = question_col[question_col != correct_answer]
        wrong_counter = Counter(wrong_answers)
        
        # Store results
        results[question_num] = {
            'correct_rate': correct_rate,
            'correct_answer': correct_answer,
            'wrong_answers': dict(wrong_counter),
            'most_common_wrong': wrong_counter.most_common(2) if wrong_counter else []
        }
    
    return results

def generate_report(results, low_performance_threshold=0.5):
    """
    Generate a report with visualizations
    """
    # Prepare data for visualizations
    questions = list(results.keys())
    correct_rates = [results[q]['correct_rate'] for q in questions]
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot 1: Correct answer rates for all questions
    sns.barplot(x=questions, y=correct_rates, ax=ax1, palette="viridis")
    ax1.axhline(y=low_performance_threshold, color='r', linestyle='--', label=f'Low performance threshold ({low_performance_threshold})')
    ax1.set_title('Correct Answer Rate by Question')
    ax1.set_xlabel('Question Number')
    ax1.set_ylabel('Correct Answer Rate')
    ax1.legend()
    
    # Add value labels on bars
    for i, v in enumerate(correct_rates):
        ax1.text(i, v + 0.01, f'{v:.2f}', ha='center', va='bottom')
    
    # Plot 2: Analysis of low performance questions
    low_perf_questions = [q for q in questions if results[q]['correct_rate'] < low_performance_threshold]
    
    if low_perf_questions:
        low_perf_data = []
        for q in low_perf_questions:
            for option, count in results[q]['wrong_answers'].items():
                low_perf_data.append({
                    'Question': f'Q{q}',
                    'Option': option,
                    'Count': count,
                    'Percentage': count / sum(results[q]['wrong_answers'].values())
                })
        
        low_perf_df = pd.DataFrame(low_perf_data)
        
        if not low_perf_df.empty:
            # Create a pivot table for the heatmap
            pivot_df = low_perf_df.pivot_table(
                values='Percentage', 
                index='Question', 
                columns='Option', 
                fill_value=0
            )
            
            # Plot heatmap
            sns.heatmap(pivot_df, annot=True, fmt='.2%', cmap='Reds', ax=ax2)
            ax2.set_title('Wrong Answer Distribution for Low Performance Questions')
        else:
            ax2.text(0.5, 0.5, 'No wrong answers for low performance questions', 
                    ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('No Data for Low Performance Questions')
    else:
        ax2.text(0.5, 0.5, 'No low performance questions', 
                ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title('No Low Performance Questions')
    
    plt.tight_layout()
    plt.savefig('student_performance_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Print textual report
    print("STUDENT PERFORMANCE ANALYSIS REPORT")
    print("*" * 50)
    
    for q in questions:
        print(f"\nQuestion {q}:")
        print(f"  Correct answer: {results[q]['correct_answer']}")
        print(f"  Correct rate: {results[q]['correct_rate']:.2%}")
        
        if results[q]['wrong_answers']:
            print("  Wrong answers distribution:")
            for option, count in results[q]['wrong_answers'].items():
                percentage = count / sum(results[q]['wrong_answers'].values())
                print(f"    {option}: {count} ({percentage:.2%})")
    
    print(f"\nLow performance questions (threshold: {low_performance_threshold:.2%}):")
    low_perf_questions = [q for q in questions if results[q]['correct_rate'] < low_performance_threshold]
    if low_perf_questions:
        for q in low_perf_questions:
            print(f"  Question {q}: {results[q]['correct_rate']:.2%} correct")
            if results[q]['most_common_wrong']:
                print(f"    Most common wrong answer(s): {results[q]['most_common_wrong']}")
    else:
        print("  No low performance questions found")

def main():
    parser = argparse.ArgumentParser(description='Analyze student multiple choice performance')
    parser.add_argument('answer_key', nargs=6, help='Correct answers for the 6 questions (space separated)')
    parser.add_argument('csv_file', help='Path to CSV file with student answers')
    parser.add_argument('--threshold', type=float, default=0.5, 
                       help='Threshold for low performance questions (default: 0.5)')
    
    args = parser.parse_args()
    
    # Analyze student performance
    results = analyze_student_performance(args.answer_key, args.csv_file, args.threshold)
    
    # Generate report and visualizations
    generate_report(results, args.threshold)

if __name__ == "__main__":
    # Example of how to run if not using command line:
    # answer_key = ['A', 'B', 'C', 'D', 'A', 'B']
    # results = analyze_student_performance(answer_key, 'student_answers.csv', 0.5)
    # generate_report(results, 0.5)
    
    main()