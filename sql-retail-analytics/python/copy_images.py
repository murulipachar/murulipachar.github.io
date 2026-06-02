import shutil
import os

def copy_screenshots():
    print("Starting screenshot copying process...")
    
    # Destination directory configuration dynamically resolved
    python_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(python_dir)
    dest_dir = os.path.join(base_dir, "screenshots")
    os.makedirs(dest_dir, exist_ok=True)
    
    # Source directory inside App Data brain folder
    src_dir = "C:\\Users\\murul\\.gemini\\antigravity\\brain\\4a231acd-d6ea-410c-a557-a61d0275a830"
    
    # Exact mappings from generated timestamps
    mappings = {
        "retail_analytics_er_diagram_1779336234218.png": "retail_analytics_er_diagram.png",
        "etl_terminal_execution_1779336252480.png": "etl_terminal_execution.png",
        "cohort_retention_heatmap_1779336271148.png": "cohort_retention_heatmap.png",
        "kpi_dashboard_summary_1779336289343.png": "kpi_dashboard_summary.png"
    }
    
    success_count = 0
    for src_name, dest_name in mappings.items():
        src_path = os.path.join(src_dir, src_name)
        dest_path = os.path.join(dest_dir, dest_name)
        
        if os.path.exists(src_path):
            shutil.copy(src_path, dest_path)
            print(f"Copied: {src_name} -> screenshots/{dest_name}")
            success_count += 1
        else:
            print(f"Error: Source image not found at {src_path}")
            
    print(f"\nSuccessfully copied {success_count} / {len(mappings)} screenshots into target directory.")

if __name__ == "__main__":
    copy_screenshots()
