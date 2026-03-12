from pathlib import Path
p = Path(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\preprocess.py')
text = p.read_text(encoding='utf-8')
text = text.replace('category_info = categorize_error(content)', "category_info = categorize_error(content, parsed['class_name'])")
text = text.replace("'feedback_items': stats['feedback_samples'][:50],", "'feedback_items': aggregate_feedback_items(stats['feedback_samples']),")
p.write_text(text, encoding='utf-8')
