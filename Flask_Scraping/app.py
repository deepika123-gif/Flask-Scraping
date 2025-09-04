from flask import Flask, render_template, url_for, redirect
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import os
import re 

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'

# Global DataFrame to hold scraped data
scraped_data = pd.DataFrame()
scraped_data_1 = pd.DataFrame()
scraped_data_2 = pd.DataFrame()
scraped_data_3 = pd.DataFrame()
scraped_data_4 = pd.DataFrame() # Added the missing global variable

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/explore') 
def explore():
    return render_template('explore.html')

@app.route('/scraping')
def scraping():
    return render_template('scraping.html')

@app.route('/scrape_1')
def scrape_1():
    global scraped_data_1
    url = "https://books.toscrape.com/catalogue/category/books/science_22/index.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    products = []
    items = soup.find_all("article", class_="product_pod")

    for item in items:
        name_tag = item.find("h3").find("a")
        price_tag = item.find("p", class_="price_color")

        name = name_tag.get("title") if name_tag else "N/A"
        price = price_tag.get_text(strip=True) if price_tag else "£0"

        
        price_text = price_tag.get_text(strip=True) if price_tag else "£0"
        price_clean = re.sub(r"[^\d.]", "", price_text)   #$4.4 -> 4.4
        price = float(price_clean) if price_clean else 0.0


        products.append([name, price])

    scraped_data_1 = pd.DataFrame(products, columns=["Name", "Price"])
    return render_template("scrape_1.html", table=scraped_data_1.to_html(index=False, classes="table table-striped"))
    
@app.route('/bar_chart')
def bar_chart():

    if scraped_data_1.empty:
        return redirect('/scrape_1')

    plt.figure(figsize=(10, 6))
    plt.bar(scraped_data_1["Name"], scraped_data_1["Price"])
    plt.xticks(rotation=90)
    plt.ylabel("Price (£)")
    plt.title("Book Prices - Bar Chart")
    chart_path = os.path.join(app.config['UPLOAD_FOLDER'], 'chart.png')
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    return render_template('bar_chart.html', chart_url=url_for('static', filename='chart.png'))

@app.route('/pie_chart')
def pie_chart():
    if scraped_data_1.empty:
        return redirect('/scrape_1')

    top_books = scraped_data_1.sort_values(by="Price", ascending=False).head(5)
    plt.figure(figsize=(8, 8))
    plt.pie(top_books["Price"], labels=top_books["Name"], autopct="%1.1f%%", startangle=140)
    plt.title("Top 5 Most Expensive Science Books")
    chart_path = os.path.join(app.config['UPLOAD_FOLDER'], 'chart.png')
    plt.savefig(chart_path)
    plt.close()
    return render_template('pie_chart.html', chart_url=url_for('static', filename='chart.png'))

@app.route('/scrape_2')
def scrape_2():
    global scraped_data_2
    url="https://quotes.toscrape.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    quotes_data=[]
    quotes=soup.find_all("div" ,class_='quote')
    for i in quotes:
      Quotes= i.find("span", class_="text").get_text(strip=True)
      Author=i.find("small",class_="author").get_text(strip=True)
      quotes_data.append ([Quotes,Author])
    # Corrected: Use scraped_data_2 and correct column names
    scraped_data_2 = pd.DataFrame(quotes_data, columns=["Quotes", "Author"])
    return render_template("scrape_2.html", table=scraped_data_2.to_html(index=False, classes="table table-striped"))

@app.route('/bar_chart_1')
def bar_chart_1():
    # Corrected: Check for scraped_data_2
    if scraped_data_2.empty:
        return redirect('/scrape_2')
    # Count the number of quotes per author
    author_counts = scraped_data_2['Author'].value_counts()
    plt.figure(figsize=(10, 6))
    # Corrected: Use the counts and their index for the bar chart
    plt.bar(author_counts.index, author_counts.values)
    plt.xticks(rotation=90)
    plt.ylabel("Number of Quotes")
    plt.title("Quotes by Author - Bar Chart")
    chart_path = os.path.join(app.config['UPLOAD_FOLDER'], 'chart_quotes_bar.png')
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    # Corrected: Use the correct chart URL
    return render_template('bar_chart_1.html', chart_url=url_for('static', filename='chart_quotes_bar.png'))

@app.route('/pie_chart_1')
def pie_chart_1():
    # Corrected: Check for scraped_data_2
    if scraped_data_2.empty:
        return redirect('/scrape_2')
    # Count the number of quotes per author
    author_counts = scraped_data_2['Author'].value_counts().head(5)
    plt.figure(figsize=(8, 8))
    # Corrected: Use the counts for the pie chart
    plt.pie(author_counts, labels=author_counts.index, autopct="%1.1f%%", startangle=140)
    plt.title("Top 5 Authors by Number of Quotes")
    chart_path = os.path.join(app.config['UPLOAD_FOLDER'], 'chart_quotes_pie.png')
    plt.savefig(chart_path)
    plt.close()
    # Corrected: Use the correct chart URL
    return render_template('pie_chart_1.html', chart_url=url_for('static', filename='chart_quotes_pie.png'))


@app.route('/scrape_3')
def scrape_3():
    global scraped_data_3
    url = 'https://www.goodreads.com/quotes'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    quotes_data = []
    quotes = soup.find_all("div", class_='quote')
    for i in quotes:
        Quotes = i.find("div", class_="quoteText")
        Author = i.find("span", class_="authorOrTitle")
        Quotes_text = Quotes.get_text(strip=True) if Quotes else "N/A"
        Author_text = Author.get_text(strip=True) if Author else "Unknown"
        quotes_data.append([Quotes_text, Author_text]) 
    scraped_data_3 = pd.DataFrame(quotes_data, columns=["Quote", "Author"])
    return render_template("scrape_3.html", table=scraped_data_3.to_html(index=False, classes="table table-striped"))

@app.route('/bar_chart_2')
def bar_chart_2():
    if scraped_data_3.empty:
        return redirect('/scrape_3')

    # Count the number of quotes per author
    author_counts = scraped_data_3['Author'].value_counts()
    
    plt.figure(figsize=(10, 6))
    # Corrected: Plot the counts
    plt.bar(author_counts.index, author_counts.values)
    plt.xticks(rotation=90)
    plt.ylabel("Number of Quotes")
    plt.title("Quotes per Author - Bar Chart")
    chart_path = os.path.join(app.config['UPLOAD_FOLDER'], 'chart3.png')
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    return render_template('bar_chart_2.html', chart_url=url_for('static', filename='chart3.png'))

@app.route('/pie_chart_2')
def pie_chart_2():
    if scraped_data_3.empty:
        return redirect('/scrape_3')

    author_counts = scraped_data_3['Author'].value_counts().head(5)

    plt.figure(figsize=(8, 8))
    plt.pie(author_counts, labels=author_counts.index, autopct="%1.1f%%", startangle=140)
    plt.title("Top 5 Authors by Number of Quotes")

    chart_path = os.path.join(app.config['UPLOAD_FOLDER'], 'chart3_pie.png')
    plt.savefig(chart_path)
    plt.close()

    return render_template('pie_chart_2.html', chart_url=url_for('static', filename='chart3_pie.png'))




@app.route('/scrape_4')
def scrape_4():
    global scraped_data_4
    url="https://www.flipkart.com/search?q=laptop&otracker=AS_Query_HistoryAutoSuggest_3_0&otracker1=AS_Query_HistoryAutoSuggest_3_0&marketplace=FLIPKART&as-show=on&as=off&as-pos=3&as-type=HISTORY"
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
     }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    laptop_data=[]
    laptop=soup.find_all("div" ,class_='tUxRFH')
    for i in laptop:
      Name= i.find("div", class_="KzDlHZ")
      Price=i.find("div",class_="Nx9bqj _4b5DiR")
      Rating=i.find("div",class_="XQDdHH")
    
      Name_text = Name.get_text(strip=True) if Name else "N/A"
      Price_text = Price.get_text(strip=True) if Price else "N/A"
      Rating_text = Rating.get_text(strip=True) if Rating else "N/A"
      
      # Corrected: Append text values inside the loop
      laptop_data.append([Name_text, Price_text, Rating_text]) 
 
    scraped_data_4 = pd.DataFrame(laptop_data, columns=["Name", "Price", "Rating"])
    return render_template("scrape_4.html", table=scraped_data_4.to_html(index=False, classes="table table-striped"))

@app.route('/bar_chart_3')
def bar_chart_3():
    # Corrected: Using the correct DataFrame and a safe check for emptiness
    if scraped_data_4 is None or scraped_data_4.empty:
        return redirect('/scrape_4')

    # Convert Price column to numeric, handling missing values
    scraped_data_4['Price_clean'] = scraped_data_4['Price'].str.replace('₹', '').str.replace(',', '').astype(float)
    
    # Plotting based on a clean, numeric 'Price' column
    plt.figure(figsize=(10, 6))
    plt.bar(scraped_data_4['Name'], scraped_data_4['Price_clean'])
    plt.xticks(rotation=90)
    plt.ylabel("Price (in INR)")
    plt.title("Laptop Prices - Bar Chart")
    
    chart_path = os.path.join(app.config['UPLOAD_FOLDER'], 'chart_Price_bar.png')
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    
    return render_template('bar_chart_3.html', chart_url=url_for('static', filename='chart_Price_bar.png'))

@app.route('/pie_chart_3')
def pie_chart_3():
    # Corrected: Using the correct DataFrame and a safe check for emptiness
    if scraped_data_4 is None or scraped_data_4.empty:
        return redirect('/scrape_4')
    
    # Corrected: Create pie chart from scraped_data_4 based on Ratings
    # Clean the rating data
    scraped_data_4['Rating_clean'] = pd.to_numeric(scraped_data_4['Rating'].str.split().str[0], errors='coerce').fillna(0)
    rating_counts = scraped_data_4['Rating_clean'].value_counts().head(5)
    
    plt.figure(figsize=(8, 8))
    plt.pie(rating_counts, labels=rating_counts.index, autopct="%1.1f%%", startangle=140)
    plt.title("Top 5 Laptop Ratings Distribution")
    
    chart_path = os.path.join(app.config['UPLOAD_FOLDER'], 'chart_ratings_pie.png')
    plt.savefig(chart_path)
    plt.close()
    
    return render_template('pie_chart_3.html', chart_url=url_for('static', filename='chart_ratings_pie.png'))






@app.route('/aboutUs')
def aboutUs():
    return render_template('about.html')


@app.route('/blogs')
def blogs():
    return render_template('blogs.html')

@app.route('/dataScience')
def dataScience():
    return render_template('scraping.html')

@app.route('/powerbi')
def powerbi():
    return render_template('powerbi.html')

@app.route('/iris_dashboard')
def iris_dashboard():
    return render_template('iris_dashboard.html')

@app.route('/titanic_deshboard')
def titanic_deshboard():
    return render_template('titanic_deshboard.html')

@app.route('/hr_deshboard')
def hr_deshboard():
    return render_template('hr_deshboard.html')

@app.route('/superstore_sales_dashboard')
def superstore_sales_dashboard():
    return render_template('superstore_sales_dashboard.html')




@app.route('/report/HR')
def report():
    return render_template("powerBIOpen.html", report_name="HR & Sales Analytics")

@app.route('/AIML')
def AIML():
    return render_template('comingSoon.html', page_name="AI/ML")

@app.route('/codroidhub')
def codroidhub():
    return render_template('codroidhub.html')



if __name__ == "__main__":
    app.run(debug=True)
