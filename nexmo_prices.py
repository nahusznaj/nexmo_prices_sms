# nexmo prices scrapping
#using the example from https://gist.github.com/dani-arancibia/768895542e91b9e170d1a87fa16e248f 

import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import pandas as pd
#import matplotlib.pyplot as plt
import matplotlib  
matplotlib.use('TkAgg')   
import matplotlib.pyplot as plt 


# This page has a list of country names and their ISO Alpha-2 code:
page_link = 'https://www.nationsonline.org/oneworld/country_code_list.htm'

#get the content from the url, using the requests library
page_response = requests.get(page_link, timeout=5)

#parsing the page
page_content = BeautifulSoup(page_response.content, "html.parser")


#get the tables from the Nations Online page
tables = page_content.find_all('table', attrs={'id': 'CountryCode'})
tables = tables[0] #this is the table that I'm interested in.

country_code = []
country_name = []

for tr in tables.find_all('tr'): 
    tds = tr.find_all('td') #get each row
    name = tds[1].get_text().strip()
    #each letter in the alphabet appears also in the table so I'll have to get rid of these:
    if len(name) > 3: #this will exclude the letters and I checked that no country has a name with length less than or equal to 3! 
        country_name.append(name)
        code = tds[2].get_text().strip() #strip will get rid of some white spaces that some countries have.
        country_code.append(code)

#some dirty checks to monitor what I'm doing:
print("Length of country code: " )
print(len(country_code)) 
print("Length of country name: ")
print(len(country_name))
print("Checking they are the same length if true: ")
print(len(country_name) == len(country_code))

#Let's have a quick look
print('Some country codes ')
print(country_code[0:10])
print('Some country codes ')
print(country_name[0:10])

################################
#### Nexmo's list of countries

### The list of countries that Nexmo works in with SMS in the list countries

url_countries = "https://www.nexmo.com/pricing"
countries_page = requests.get(url_countries)
page_content = BeautifulSoup(countries_page.content, "html.parser")

nexmo_countries_list = []
for foo in page_content.find_all('div', attrs={'class': 'dropdown-row'}):
    nexmo_countries_list.append(foo.get_text())

# Comparing with the total list of countries

## Let's compare the list of countries that I got from the Nations Online page and the list of countries from Nexmo.

print("Length of nexmo_country_list: ")

print(len(nexmo_countries_list))

nn = set(nexmo_countries_list)
no = set(country_name)

difference = no.union(nn)  - no.intersection(nn)

print("Length of the differnce between nexmo_coutnry_list and country_name: " )
print(len(difference))  #this means that there's something else going on :( 
print("print the difference" )
print(difference) # So many countries are different. Although to make things not as bad, the list from wikipedia was much different than this, it took me a while to realised I was better off finding a more similar table of countries!


#I see two sources of differences between the countries list from Nexmo and the source from the Nations Online: 1) the way the name is written, such as "Viet Nam" or "Vietnam", and 2) whether genuinely Nexmo does not operate in a country that does have a code, such as in  'South Georgia and the South Sandwich Islands' (let's test this last claim).


if 'South Georgia and the South Sandwich Islands' in country_name:
        print("Some little islands in the south atlantic")

if 'South Georgia and the South Sandwich Islands' not in nexmo_countries_list:
        print("Nexmo is coming soon!")


modified_nexmo_countries_list = []
for item in nexmo_countries_list:
    modified_nexmo_countries_list.append(item.replace('&', 'and'))

    #This is one quick fix I can make on the go.

print("Some of the coutnries in the modified list: ")
print(modified_nexmo_countries_list[0:10])

print("And the length")
print(len(modified_nexmo_countries_list))

nn = set(modified_nexmo_countries_list)
no = set(country_name)

difference = no.union(nn)  - no.intersection(nn)
print("Length of the difference now")
print(len(difference)) 
print("List of countries that are not common" )
print(difference) #This shows the other differences in naming countries.



### At the moment I will continue and leave this for later. It took me a lot of time to be able to get this table. I had spent some time working with the table from [wikipedia](https://en.wikipedia.org/wiki/ISO_3166-1), which is a lot more different to the one Nexmo is using than this one!

### Let's try and continue and work with the pricing page itself:

### The url for the pricing per country has a formula like: 

#### `url_basic = "https://rest.nexmo.com/pricing/messaging/"` + `COUNTRY_CODE/jsonp?`

### I will use the country code with the lists that I created earlier. First, I'll create a dictionary, where I have the country name as key and the country code as value. Then I will compare the list of countries from Nexmo with the dictionary to obtain the right country code.

code_per_country = {}
for number, item in enumerate(country_name): #ignore the header in this table
    code_per_country[item] = country_code[number]
    
    
#print(code_per_country)

#some checking just in case...
print("#some checking just in case: ")
print(len(code_per_country) == len(country_code) == len(country_name))


##The reason for the next move is that I want to use the international codes for the countries that Nexmo operates in. If I put a wrong code it'll be an invalid URL and the requests.get will give me an error 404 or 500. (I tried and that's what happened, try https://rest.nexmo.com/pricing/messaging/AN/jsonp? and let me know)

url_ending = []
back_up_country_list = [] #


for item in country_name:
    if item in modified_nexmo_countries_list: 
        back_up_country_list.append(item)
        url_ending.append(code_per_country[item] + "/jsonp?")


#print(url_ending)
#print(back_up_country_list)

print(len(url_ending) == len(back_up_country_list))

print(len(url_ending))

url_basic = "https://rest.nexmo.com/pricing/messaging/"
country_list= []
out_SMS_price = []
total_output = []
counter = 0

#I encountered some errors so I skipped one country that was problematic ('Netherlands Antilles'!). I'm sure this can be optimised! This is a cheap and easy solution.

new_url_list = url_ending[0:134] + url_ending[135:]

print(len(new_url_list))

#let's have a look at the pricing output:
print(total_output[0:5])

# so it's a list of nested dictionaries.

## Comments on the data in `total_output`

## I am aware that this is not ideal. I started off with 232 countries mentioned in the website url_countries = "https://www.nexmo.com/pricing". But I got pricing for 204. I know one of them has an error, 'Netherlands Antilles'. And, indeed, when you visit the pricing webpage and search for Netherlands Antilles you realise there's something wrong there.

## I know I'm leaving on the side other countries, like Vietnam, because of incomatibilities in the names for the countries. Maybe there was an easier way to pull the list of countries. If I had more time I would manually change them.
# 
# # There are still 27 countries that I couldn't get pricing for. I think this is due to spelling differences, as mentioned above. 

# So, for the purpose of this exercise I will leave this as it is now and continue with the analysis. There's still a bit to do: create a pandas data frame, clean the data, and analyse it.

#This is the work with Nexmo's webpage.

for item in new_url_list:
    url_country = url_basic + item
    print(url_country) #to check progress!!!
    html_page = requests.get(url_country, timeout=15)
    country_dict = html_page.json()
    total_output.append(country_dict)
    counter += 1
    time.sleep(5)


print(counter)

## Comments on the data in `total_output`

# This is not ideal. I started off with 232 countries mentioned in the website url_countries = "https://www.nexmo.com/pricing". But I got pricing for 204. I know one of them has an error, 'Netherlands Antilles'. And, indeed, when you visit the pricing webpage and search for Netherlands Antilles you realise there's something wrong there.

# There are still 27 countries that I couldn't get pricing for. I think this is due to spelling differences, as mentioned above. 

# I would change them mannually, but for the purpose of this exercise I will leave it as is now and continue with the analysis. There's still a bit to do: create a pandas data frame, clean the data, and analyse it.


### Now some analysis with pandas:

df = pd.DataFrame(data = ((key["country"], 
                           key['name'], 
                           key["messaging"],
                          key['messaging']['outbound']) for key in total_output),  
                  columns = ("country_code", "name", "messaging", 'currency'))


print(df.head())

## The information is somewhat inconsisten... some countries don't have a flatMobilePrice, so I'll arrange the dictionary in Currency to have a value for the key 'flatMobilPrice'. This is the bit of the pricing I will look into, althouh I appreciate that more work should be done if I had more time for this project.


# This will make sure that all rows in the dataframe have a value for flatMobilePrice

for key in df.currency:
    if 'flatMobilePrice' not in key:
        key['flatMobilePrice'] = '0'

price_SMS = [] #I will then add this to the dataframe
for i in df.currency.iloc[:]:
    price_SMS.append(i['flatMobilePrice'])


sms_price =pd.Series(price_SMS)
df['SMS_price'] = sms_price.values

print(df.head())


# Now this is looking like something I could work with! 


# What I'll do is to run some stats on the prices for flatMobilePrice. The sequence of code above could be repeated to include other details. I'll leave for future.


print(df.info())

df.SMS_price = pd.to_numeric(df.SMS_price, errors='ignore')

print(df.info())


# Maximum and minimum price:

print(df[['name', 'SMS_price']][df.SMS_price==df.SMS_price.max()])

print(df[['name', 'SMS_price']][df.SMS_price==df.SMS_price.min()])


print(df.SMS_price.describe())

# So, for the sample that I have (the population would include the rest of the countries that I couldn't pick up),  the mean price is 0.051182 EUR.

# The standard deviation is  0.028743 EUR
# the minimum price is 0.000000, free :D
# the maximum price 16 cents EUR.
# The quintiles are set as 
# min        0.000000
# 25%        0.032625
# 50%        0.048050
# 75%        0.070000
# max        0.160000

fix, ax = plt.subplots(figsize = (10,7))

plt.suptitle('Distribution of prices for outbound SMS', fontsize = 16)
plt.boxplot(df.SMS_price)
plt.axhline(y=df.SMS_price.max(), linewidth=1, color = 'b', label = 'max')
plt.axhline(y=df.SMS_price.mean(), linewidth=1, color = 'r', label = 'mean')
plt.axhline(y=df.SMS_price.min(), linewidth=1, color = 'g', label = 'min')
ax.set_ylabel('Price (EUR)', fontsize = 14)
ax.get_xticklabels( 'SMS price')

plt.legend(fontsize = 12)
plt.show()