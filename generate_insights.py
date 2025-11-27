import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

# Create charts directory
Path("charts").mkdir(exist_ok=True)

# Load data
print("Loading data...")
df = pd.read_csv('ebooks_az_all_books_detailed.csv')

print(f"Total books loaded: {len(df)}")
print(f"Columns: {df.columns.tolist()}")

# Clean data
df['year'] = pd.to_numeric(df['year'], errors='coerce')
df['page_count'] = pd.to_numeric(df['page_count'], errors='coerce')

# Filter valid years (1900-2025)
df_year_filtered = df[(df['year'] >= 1900) & (df['year'] <= 2025)]

print(f"\nBooks with valid years: {len(df_year_filtered)}")
print(f"Year range: {df_year_filtered['year'].min():.0f} - {df_year_filtered['year'].max():.0f}")

# Generate insights dictionary
insights = {}

# 1. Top 15 Categories by Book Count (Bar Chart - Horizontal for better readability)
print("\nGenerating category distribution chart...")
category_counts = df['category'].value_counts().head(15)
insights['top_category'] = category_counts.index[0]
insights['top_category_count'] = category_counts.values[0]
insights['total_categories'] = df['category'].nunique()

plt.figure(figsize=(12, 8))
colors = sns.color_palette("viridis", len(category_counts))
bars = plt.barh(range(len(category_counts)), category_counts.values, color=colors)
plt.yticks(range(len(category_counts)), category_counts.index)
plt.xlabel('Number of Books', fontsize=12, fontweight='bold')
plt.ylabel('Category', fontsize=12, fontweight='bold')
plt.title('Top 15 Categories by Number of Books', fontsize=14, fontweight='bold', pad=20)
plt.gca().invert_yaxis()

# Add value labels
for i, (idx, value) in enumerate(category_counts.items()):
    plt.text(value + 20, i, f'{value:,}', va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/01_category_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# 2. Publication Trends Over Time (Line Chart)
print("Generating publication trends chart...")
yearly_counts = df_year_filtered['year'].value_counts().sort_index()
insights['most_productive_year'] = yearly_counts.idxmax()
insights['most_productive_year_count'] = yearly_counts.max()
insights['recent_5yr_avg'] = yearly_counts.tail(5).mean()

plt.figure(figsize=(14, 6))
plt.plot(yearly_counts.index, yearly_counts.values, linewidth=2.5, color='#2E86AB', marker='o', markersize=3)
plt.fill_between(yearly_counts.index, yearly_counts.values, alpha=0.3, color='#2E86AB')
plt.xlabel('Year', fontsize=12, fontweight='bold')
plt.ylabel('Number of Books Published', fontsize=12, fontweight='bold')
plt.title('Publication Trends Over Time (1900-2025)', fontsize=14, fontweight='bold', pad=20)
plt.grid(True, alpha=0.3)

# Add trend line
z = np.polyfit(yearly_counts.index, yearly_counts.values, 1)
p = np.poly1d(z)
plt.plot(yearly_counts.index, p(yearly_counts.index), "--", alpha=0.8, color='red', linewidth=2, label='Trend Line')
plt.legend()

plt.tight_layout()
plt.savefig('charts/02_publication_trends.png', dpi=300, bbox_inches='tight')
plt.close()

# 3. Top 15 Publishers (Horizontal Bar Chart)
print("Generating top publishers chart...")
publisher_counts = df[df['publisher'].notna() & (df['publisher'] != '')]['publisher'].value_counts().head(15)
insights['top_publisher'] = publisher_counts.index[0] if len(publisher_counts) > 0 else "N/A"
insights['top_publisher_count'] = publisher_counts.values[0] if len(publisher_counts) > 0 else 0

plt.figure(figsize=(12, 8))
colors = sns.color_palette("rocket", len(publisher_counts))
bars = plt.barh(range(len(publisher_counts)), publisher_counts.values, color=colors)
plt.yticks(range(len(publisher_counts)), publisher_counts.index, fontsize=9)
plt.xlabel('Number of Books', fontsize=12, fontweight='bold')
plt.ylabel('Publisher', fontsize=12, fontweight='bold')
plt.title('Top 15 Publishers by Number of Books', fontsize=14, fontweight='bold', pad=20)
plt.gca().invert_yaxis()

# Add value labels
for i, (idx, value) in enumerate(publisher_counts.items()):
    plt.text(value + 5, i, f'{value:,}', va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/03_top_publishers.png', dpi=300, bbox_inches='tight')
plt.close()

# 4. Top 15 Authors (Horizontal Bar Chart)
print("Generating top authors chart...")
author_counts = df[df['author'].notna() & (df['author'] != '')]['author'].value_counts().head(15)
insights['top_author'] = author_counts.index[0] if len(author_counts) > 0 else "N/A"
insights['top_author_count'] = author_counts.values[0] if len(author_counts) > 0 else 0

plt.figure(figsize=(12, 8))
colors = sns.color_palette("mako", len(author_counts))
bars = plt.barh(range(len(author_counts)), author_counts.values, color=colors)
plt.yticks(range(len(author_counts)), author_counts.index, fontsize=9)
plt.xlabel('Number of Books', fontsize=12, fontweight='bold')
plt.ylabel('Author', fontsize=12, fontweight='bold')
plt.title('Top 15 Most Prolific Authors', fontsize=14, fontweight='bold', pad=20)
plt.gca().invert_yaxis()

# Add value labels
for i, (idx, value) in enumerate(author_counts.items()):
    plt.text(value + 0.5, i, f'{value:,}', va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/04_top_authors.png', dpi=300, bbox_inches='tight')
plt.close()

# 5. Recent Publication Trends (Last 10 Years - Line Chart)
print("Generating recent publication trends...")
recent_years = df_year_filtered[df_year_filtered['year'] >= 2015]
recent_yearly = recent_years['year'].value_counts().sort_index()
insights['last_year_count'] = recent_yearly.get(recent_yearly.index.max(), 0) if len(recent_yearly) > 0 else 0

plt.figure(figsize=(12, 6))
plt.plot(recent_yearly.index, recent_yearly.values, linewidth=3, color='#06D6A0', marker='o', markersize=8)
plt.fill_between(recent_yearly.index, recent_yearly.values, alpha=0.3, color='#06D6A0')
plt.xlabel('Year', fontsize=12, fontweight='bold')
plt.ylabel('Number of Books Published', fontsize=12, fontweight='bold')
plt.title('Recent Publication Trends (2015-2025)', fontsize=14, fontweight='bold', pad=20)
plt.grid(True, alpha=0.3)

# Add value labels
for x, y in zip(recent_yearly.index, recent_yearly.values):
    plt.text(x, y + 10, str(int(y)), ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/05_recent_trends.png', dpi=300, bbox_inches='tight')
plt.close()

# 6. Page Count Distribution (Histogram)
print("Generating page count distribution...")
page_data = df[df['page_count'].notna() & (df['page_count'] > 0) & (df['page_count'] < 2000)]
insights['avg_page_count'] = page_data['page_count'].mean()
insights['median_page_count'] = page_data['page_count'].median()

plt.figure(figsize=(12, 6))
plt.hist(page_data['page_count'], bins=50, color='#F72585', edgecolor='black', alpha=0.7)
plt.axvline(insights['avg_page_count'], color='blue', linestyle='--', linewidth=2, label=f'Mean: {insights["avg_page_count"]:.0f} pages')
plt.axvline(insights['median_page_count'], color='green', linestyle='--', linewidth=2, label=f'Median: {insights["median_page_count"]:.0f} pages')
plt.xlabel('Number of Pages', fontsize=12, fontweight='bold')
plt.ylabel('Number of Books', fontsize=12, fontweight='bold')
plt.title('Distribution of Book Page Counts', fontsize=14, fontweight='bold', pad=20)
plt.legend()
plt.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('charts/06_page_count_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# 7. Publication Place Distribution (Top 10)
print("Generating publication place chart...")
place_counts = df[df['publication_place'].notna() & (df['publication_place'] != '')]['publication_place'].value_counts().head(10)
insights['top_publication_place'] = place_counts.index[0] if len(place_counts) > 0 else "N/A"
insights['top_publication_place_count'] = place_counts.values[0] if len(place_counts) > 0 else 0

plt.figure(figsize=(12, 6))
colors = sns.color_palette("crest", len(place_counts))
bars = plt.barh(range(len(place_counts)), place_counts.values, color=colors)
plt.yticks(range(len(place_counts)), place_counts.index)
plt.xlabel('Number of Books', fontsize=12, fontweight='bold')
plt.ylabel('Publication Place', fontsize=12, fontweight='bold')
plt.title('Top 10 Publication Places', fontsize=14, fontweight='bold', pad=20)
plt.gca().invert_yaxis()

# Add value labels
for i, (idx, value) in enumerate(place_counts.items()):
    plt.text(value + 20, i, f'{value:,}', va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/07_publication_places.png', dpi=300, bbox_inches='tight')
plt.close()

# 8. Category-Year Heatmap (Top 10 categories, last 10 years)
print("Generating category-year heatmap...")
top_10_cats = df['category'].value_counts().head(10).index
recent_df = df_year_filtered[df_year_filtered['year'] >= 2015]
heatmap_data = recent_df[recent_df['category'].isin(top_10_cats)].groupby(['category', 'year']).size().unstack(fill_value=0)

plt.figure(figsize=(14, 8))
sns.heatmap(heatmap_data, annot=True, fmt='d', cmap='YlOrRd', cbar_kws={'label': 'Number of Books'}, linewidths=0.5)
plt.xlabel('Year', fontsize=12, fontweight='bold')
plt.ylabel('Category', fontsize=12, fontweight='bold')
plt.title('Publication Heatmap: Top 10 Categories (2015-2025)', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('charts/08_category_year_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()

# Generate summary statistics
print("\n" + "="*60)
print("DATA INSIGHTS SUMMARY")
print("="*60)
print(f"\nTotal Books Scraped: {len(df):,}")
print(f"Total Categories: {insights['total_categories']}")
print(f"Date Range: {df_year_filtered['year'].min():.0f} - {df_year_filtered['year'].max():.0f}")
print(f"\nTop Category: {insights['top_category']} ({insights['top_category_count']:,} books)")
print(f"Top Publisher: {insights['top_publisher']} ({insights['top_publisher_count']:,} books)")
print(f"Top Author: {insights['top_author']} ({insights['top_author_count']:,} books)")
print(f"\nMost Productive Year: {insights['most_productive_year']:.0f} ({insights['most_productive_year_count']:,} books)")
print(f"Recent 5-Year Average: {insights['recent_5yr_avg']:.1f} books/year")
print(f"\nAverage Page Count: {insights['avg_page_count']:.0f} pages")
print(f"Median Page Count: {insights['median_page_count']:.0f} pages")
print(f"\nTop Publication Place: {insights['top_publication_place']} ({insights['top_publication_place_count']:,} books)")
print("\n" + "="*60)

# Save insights to file
with open('charts/insights_summary.txt', 'w', encoding='utf-8') as f:
    f.write("="*60 + "\n")
    f.write("EBOOKS.AZ DATA INSIGHTS SUMMARY\n")
    f.write("="*60 + "\n\n")
    f.write(f"Total Books Scraped: {len(df):,}\n")
    f.write(f"Total Categories: {insights['total_categories']}\n")
    f.write(f"Date Range: {df_year_filtered['year'].min():.0f} - {df_year_filtered['year'].max():.0f}\n\n")
    f.write(f"Top Category: {insights['top_category']} ({insights['top_category_count']:,} books)\n")
    f.write(f"Top Publisher: {insights['top_publisher']} ({insights['top_publisher_count']:,} books)\n")
    f.write(f"Top Author: {insights['top_author']} ({insights['top_author_count']:,} books)\n\n")
    f.write(f"Most Productive Year: {insights['most_productive_year']:.0f} ({insights['most_productive_year_count']:,} books)\n")
    f.write(f"Recent 5-Year Average: {insights['recent_5yr_avg']:.1f} books/year\n\n")
    f.write(f"Average Page Count: {insights['avg_page_count']:.0f} pages\n")
    f.write(f"Median Page Count: {insights['median_page_count']:.0f} pages\n\n")
    f.write(f"Top Publication Place: {insights['top_publication_place']} ({insights['top_publication_place_count']:,} books)\n")

print("\nAll charts saved to 'charts/' directory")
print("Insights summary saved to 'charts/insights_summary.txt'")
