import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

df = pd.read_csv('PRODUCTS.txt', header=None, names=['Product', 'Brand1', 'Brand2', 'Brand3'])
stock_df = pd.read_csv('stocks.txt', header=None, names=['Brand', 'Stock'])

daily_purchases = {
    'SOAP': [0, 0, 0],  
    'SHAMPOO': [0, 0, 0],
    'TOOTHPASTE': [0, 0, 0],
    'HANDWASH': [0, 0, 0],
    'COFFEE': [0, 0, 0],
    'TEA': [0, 0, 0]
}

history_dir = "D:/Spyder/Semester 3/package2"

def plotStockLevels():
    
    products = ["Soap","Shampoo","Toothpaste","Handwash","Coffee","Tea"]
    
    num_products = len(products)
    for page in range(0, num_products, 2):
        fig, axes = plt.subplots(2, 1, figsize=(8, 10))
        
        for i in range(0,2):
            product = products[page + i]
            history_filename = os.path.join(history_dir, f'history{product}.txt')
            if os.path.exists(history_filename):
                data = np.genfromtxt(history_filename, delimiter=',', dtype='str')
                days = np.array([int(day[1:]) for day in data[:, 0]])  # Remove 'D' and convert to integers
                stock_levels = data[:, 1:].astype(int)

                ax = axes[i]
                
                for j in range(stock_levels.shape[1]):  
                    ax.plot(days, stock_levels[:, j], label=f'Brand {j+1}')

                ax.set_xlabel('Day')
                ax.set_ylabel('Stock Levels')
                ax.set_title(f'Stock Levels Over Time for {product}')
                ax.legend()
                ax.grid()
            else:
                print(f"File {history_filename} not found!")
        plt.tight_layout()
        plt.show()

day_counter = 1

def reduceStock(brand, quantity):
    if brand in stock_df['Brand'].values:
        currentStock = stock_df.loc[stock_df['Brand'] == brand, 'Stock'].values[0]
        if currentStock >= quantity:
            stock_df.loc[stock_df['Brand'] == brand, 'Stock'] -= quantity
            print("\n", quantity, "units of", brand, "purchased. Remaining stock:", currentStock - quantity)
            
            logDailyPurchase(brand, quantity)
            
        else:
            print("\nInsufficient stock for", brand, ". Only", currentStock, "units available.")
    else:
        print("\nBrand", brand, "not found in stock.")


    stock_df.to_csv('stocks.txt', header=False, index=False)

def logDailyPurchase(brand, quantity):
    products = ['SOAP', 'SHAMPOO', 'TOOTHPASTE', 'HANDWASH', 'COFFEE', 'TEA']
    
    for product in products:
        if brand in df.loc[df['Product'] == product, ['Brand1', 'Brand2', 'Brand3']].values:
            index = df.loc[df['Product'] == product, ['Brand1', 'Brand2', 'Brand3']].values[0].tolist().index(brand)
            daily_purchases[product][index] += quantity

def loadDayCounter():
    if os.path.exists('day_counter.txt'):
        try:
            with open('day_counter.txt', 'r') as file:
                return int(file.read().strip())
        except (ValueError, IOError):
            print("Error reading day counter file. Starting from Day 1.")
            return 1
    else:
        return 1

def saveDayCounter(day_counter):
    try:
        with open('day_counter.txt', 'w') as file:
            file.write(str(day_counter))
    except IOError as e:
        print(f"Error saving day counter: {e}")

def rewriteDayInHistoryFile(product, day_counter, stock_list):
    filename = f'history{product}.txt'
    lines = []
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                lines = file.readlines()

        day_found = False
        with open(filename, 'w') as file:
            for line in lines:
                if line.startswith(f"D{day_counter},"):
                    file.write(f"D{day_counter}," + ",".join(map(str, stock_list)) + "\n")
                    day_found = True
                else:
                    file.write(line)
            
            if not day_found:
                file.write(f"D{day_counter}," + ",".join(map(str, stock_list)) + "\n")
    except IOError as e:
        print(f"Error updating file {filename}: {e}")

def endOfDay(runNextDay=False):
    global day_counter

    day_counter = loadDayCounter()

    products = ['SOAP', 'SHAMPOO', 'TOOTHPASTE', 'HANDWASH', 'COFFEE', 'TEA']

    for product in products:
        stock_list = stock_df.loc[stock_df['Brand'].isin(df.loc[df['Product'] == product, ['Brand1', 'Brand2', 'Brand3']].values[0]), 'Stock'].tolist()
        
        print(f"Rewriting history{product.title()}.txt for Day {day_counter}: " + ",".join(map(str, stock_list)))
        rewriteDayInHistoryFile(product, day_counter, stock_list)

    if runNextDay:
        day_counter += 1
        saveDayCounter(day_counter)

    for product in products:
        daily_purchases[product] = [0, 0, 0]

day_counter = loadDayCounter()
user_purchases={}
def purchase_item(brand, quantity):
    if brand in stock_df['Brand'].values:
        current_stock = stock_df.loc[stock_df['Brand'] == brand, 'Stock'].values[0]        
        if current_stock >= quantity:
            stock_df.loc[stock_df['Brand'] == brand, 'Stock'] -= quantity            
            if brand in user_purchases:
                user_purchases[brand] += quantity
            else:
                user_purchases[brand] = quantity 
            print(f"\n{quantity} units of {brand} purchased. Remaining stock: {current_stock - quantity}")
        else:
            print(f"\nInsufficient stock for {brand}. Only {current_stock} units available.")
    else:
        print(f"\nBrand {brand} not found in stock.")
    stock_df.to_csv('stocks.txt', header=False, index=False)


def display_purchases():
    print("\n\t\t\tYour Purchases")
    for brand, quantity in user_purchases.items():
        print(f"  {brand}: {quantity} units")

def user():
    while(1):
        print("\n\t\t\t\tAvailable Products")
        print(df['Product'])
    
        choice = input("\nEnter choice to see the brands: ")
        if choice.isdigit():
            choice = int(choice)
            if 0 <= choice < len(df):
                print("\n\t\t\t\tBrands for", df.loc[choice, 'Product'])
                print(df.loc[choice, ['Brand1', 'Brand2', 'Brand3']].to_string(index=False))
                selectedBrand = input("\nEnter the brand you want to buy: ")
                quantity = int(input("Enter the quantity to purchase: "))
                
                reduceStock(selectedBrand, quantity)
            else:
                print("Invalid number. Please try again.")
        else:
            print("Invalid input. Please enter a valid number.")
        purchase_item(selectedBrand, quantity)
        inp = input("Do you want to go to the home page? (y/n): ").lower()
        if inp == 'y':
            display_purchases()  
            home()
            

def load_products_and_brands(products_file):
    product_brand_map = {}
    with open(products_file, 'r') as file:
        lines = file.readlines()
    
    for line in lines:
        parts = line.strip().split(',') 
        product = parts[0]  
        brands = parts[1:] 
        product_brand_map[product] = brands
    
    return product_brand_map

def load_brand_stocks(stocks_file):
    brand_stock_map = {}
    with open(stocks_file, 'r') as file:
        lines = file.readlines()
    
    for line in lines:
        brand, stock = line.strip().split(',') 
        brand_stock_map[brand] = int(stock)  
    
    return brand_stock_map

def calculate_total_inventory(products_file, stocks_file):
    product_brand_map = load_products_and_brands(products_file)
    brand_stock_map = load_brand_stocks(stocks_file)
    for product, brands in product_brand_map.items():
        total_stock = 0
        print(f"Product: {product}")
        
        for brand in brands:
            if brand in brand_stock_map:
                total_stock += brand_stock_map[brand]
                print(f"  {brand}: {brand_stock_map[brand]}")
            else:
                print(f"  {brand}: Stock data not found")
        
        print(f"Total stock for {product}: {total_stock}\n")
    
def restock():
    brand = input("\nEnter the brand to restock: (CAPS)")
    if brand in stock_df['Brand'].values:
        try:
            quantity = int(input(f"Enter the quantity to restock for {brand}: "))
            
            if quantity > 0:
                current_stock = stock_df.loc[stock_df['Brand'] == brand, 'Stock'].values[0]
                new_stock = current_stock + quantity
                stock_df.loc[stock_df['Brand'] == brand, 'Stock'] = new_stock
                stock_df.to_csv('stocks.txt', header=False, index=False)
                
                print(f"\n{quantity} units added to {brand}. New stock: {new_stock} units.")
            else:
                print("\nInvalid quantity. Please enter a positive number.")
        except ValueError:
            print("\nInvalid input. Please enter a valid number for quantity.")
    else:
        print("\nBrand not found in the stock list.")

    
    
def viewStock():    
    print("\n\t\t\t\tCurrent Stock Levels")
    print(stock_df.to_string(index=False))
    
def plotMarkovChainPredictions(stockForecast, random_stock_forecast, daysToPredict, restock_days):
    fig, ax = plt.subplots()
    for i in range(3):
        ax.plot(range(daysToPredict + 1), [day[i] for day in random_stock_forecast], label=f'Brand {i+1} (Quantities)')

    for restock_day, brand in restock_days:
        ax.scatter(restock_day, random_stock_forecast[restock_day][brand], color='red', zorder=5, label=f'Restock Brand {brand+1} on Day {restock_day}')

    ax.set_xlabel('Day')
    ax.set_ylabel('Stock Quantities')
    ax.set_title('Stock Quantities Forecast Using Markov Chains')
    ax.legend()
    ax.grid()
    plt.show()

def predictUsingMarkovChains(transition_matrix, productName, daysToPredict):
    initialState = [0.27, 0.45, 0.20]
    stockForecast = [initialState]
    for day in range(daysToPredict):
        new_stock = np.dot(transition_matrix, stockForecast[-1])
        stockForecast.append(new_stock)

    print("\nStock Forecast for Next", daysToPredict, "days about stock state (in %):")
    for day, stocks in enumerate(stockForecast):
        print(f"Day {day}: {stocks}")
   
    initial_stock = [30, 30, 30]  
    total_stock_capacity = [55, 55, 55]  
    random_stock_forecast = []
    restock_days = [] 
    current_stock = initial_stock.copy()  

    for day, probs in enumerate(stockForecast):
        stock_quantities = []
        for brand in range(3):
            stock_quantity = current_stock[brand] 

            if stock_quantity < 5:
                stock_quantity += 50  
                restock_days.append((day, brand)) 

            stock_quantity = min(stock_quantity, total_stock_capacity[brand])  
            stock_quantities.append(stock_quantity)

            current_stock[brand] = stock_quantity - np.random.randint(0, 10)  # Simulate sales (random reduction)

        random_stock_forecast.append(stock_quantities)

    print("\nStock Quantities Forecast using Transition Matrix and Markov Chains:")
    for day, stocks in enumerate(random_stock_forecast):
        print(f"Day {day}: {stocks}")

    print("\n\t\tPredicted Daily Statistics and Analysis:")
    for day in range(len(random_stock_forecast)):
        stocks = random_stock_forecast[day]
        print(f"\nDay {day} Statistics:")
        
        for brand in range(3):
            print(f"  Brand {brand + 1}: {stocks[brand]} units")
        if day > 0:
            previous_day_sales = random_stock_forecast[day - 1]
            sold_better_brand = None
            max_sales_difference = -1
            total_sales_today = sum(previous_day_sales) - sum(stocks)

            for brand in range(3):
                sales_difference = previous_day_sales[brand] - stocks[brand]
                if sales_difference > max_sales_difference:
                    max_sales_difference = sales_difference
                    sold_better_brand = brand + 1

            if sold_better_brand:
                print(f"  Brand {sold_better_brand} sold better compared to Day {day}.")
            else:
                if total_sales_today < 0:
                    print("  Stock increased without a corresponding sales decrease (possible restock).")
                else:
                    print("  No brand sold better compared to the previous day, and stocks decreased or remained stable.")
        else:
            print("  This is the first day of forecast.")

    if restock_days:
        print("\nRestock would be required on the following days for respective brands:")
        for day, brand in set(restock_days): 
            print(f"  Day {day} for Brand {brand+1}")
    else:
        print("\nNo restock would be required during the forecast period.")
    
    plotMarkovChainPredictions(stockForecast, random_stock_forecast, daysToPredict, restock_days)


    
def admin():
    while True:
        print("\n\t\t\tADMIN PANEL")
        print("1. Log the day's summary?")
        print("2. Restock an existing brand")
        print("3. View current stock levels")
        print("4. Calculate total inventory")
        print("5. Predict future stock levels using Markov Chains")
        print("6. Exit")

        choice = input("\nEnter your choice (1-8): ").strip()

        if choice == '1':
            inp = input("\nDo you want to exit and log the day's summary? (y/n): ")
            if inp.lower() == 'y':
                next_day = input("Do you want to start a new day (y/n)? ").lower()
                if next_day == 'y':
                    print("Logging the day’s stock summary and moving to the next day...")
                    endOfDay(runNextDay=True) 
                else:
                    print("Logging the current day’s stock summary...")
                    endOfDay() 
                print("Thank you for purchasing!")
                admin()
                break
              
        elif choice == '2':
            restock()
        elif choice == '3':
            viewStock()
        elif choice == '4':
            products_file = 'PRODUCTS.txt'
            stocks_file = 'stocks.txt'
            calculate_total_inventory(products_file, stocks_file)
             
        elif choice == '5':
            
            product = input("Enter product name to predict future stock levels : ")
            noOfDays = int(input("Enter number of days to predict : "))
           
            file_path = f"D:/Spyder/Semester 3/PACKAGE FINAL/history{product.title()}.txt"

            historical_data = np.genfromtxt(file_path, delimiter=',', usecols=(1, 2, 3))

            transition_counts = {
                1: {"LL": 0, "SS": 0, "LH":0},
                2: {"LL": 0, "SS": 0, "LH":0},
                3: {"LL": 0, "SS": 0, "LH":0}}

            for i in range(1, len(historical_data)):  
                for brand in range(3):
                    prev_stock = historical_data[i - 1][brand]
                    curr_stock = historical_data[i][brand]

                    if curr_stock<5:
                        transition_counts[brand + 1]["LH"] +=1
                        historical_data[i][brand] += 50 
                    elif curr_stock < prev_stock:
                        transition_counts[brand + 1]["LL"] += 1 
                    elif curr_stock == prev_stock:  
                        transition_counts[brand + 1]["SS"] += 1
            print("\n\t\tTransition Counts:")
            for brand in range(1, 4):
                print(f"Brand {brand}: {transition_counts[brand]}")

            transition_matrix = []
            for brand in range(1, 4):
                total_transitions = sum(transition_counts[brand].values())
                
                if total_transitions > 0:
                    ll = transition_counts[brand]["LL"] / total_transitions
                    ss = transition_counts[brand]["SS"] / total_transitions
                    lh = transition_counts[brand]["LH"] / total_transitions
                    transition_matrix.append([ll,ss,lh])
                else:
                    transition_matrix.append([0.5, 0.5, 0.5]) 

            transition_matrix = np.array(transition_matrix)
            print("\n\t\tTransition Matrix:")
            print(transition_matrix)
            
            predictUsingMarkovChains(transition_matrix,product,noOfDays)      
                
        elif choice == '6':
            plotStockLevels()
            home()

        else:
            print("Invalid choice. Please try again.")

def home():
    
    print("\n\t\t\t\t\tINVENTORY MANAGEMENT\n")
    ch = int(input("\n1 - ADMIN\n2 - CUSTOMER\nEnter choice : "))
    if ch==1:
        admin()
    else:
        user()
home()
