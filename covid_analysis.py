#!/usr/bin/env python
# coding: utf-8

# # Wczytanie danych w postaci czasowej

# Zrezygnowałem z pobierania danych z COVID API, gdyż niepotrzebne jest odświeżanie danych co kilka minut. Każdy kraj i tak raz dziennie publikuje oficjalne statystyki, więc dane można pobierać wyłącznie ze źródeł "offline".
# 
# Na początku dane pobrałem z https://github.com/CSSEGISandData/COVID-19 

# In[24]:


import requests
import pandas as pd

url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
r = requests.get(url, allow_redirects=True)
open('time_series.csv', 'wb').write(r.content)

url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
r = requests.get(url, allow_redirects=True)
open('deaths.csv', 'wb').write(r.content)

url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'
r = requests.get(url, allow_redirects=True)
open('recovered.csv', 'wb').write(r.content)


# In[25]:


cases = pd.read_csv("time_series.csv")
deaths = pd.read_csv("deaths.csv")
recovered = pd.read_csv("recovered.csv")
cases.tail()


# In[26]:


deaths.tail()


# In[27]:


recovered.tail()


# Dane powyżej są mniej szczegółowe, dotyczą 265 (w przypadku recovered mniej) regionów i zawierają informacje historyczne z każdego dnia - przydatne do tworzenia wykresów. Bonusem jest fakt, iż codzinennie aktualizowany jest ten sam plik, a nie dodawany nowy, więc wystarczy pobrać z tego samego linku.

# # Dane z dziennych raportów

# Następnie pobrałem raport dzienny z tego samego źródła danych. Stworzyłem zmienną do przechowywania dzisiejszej (lub wczorajszej, gdyż raporty za dany dzień są wystawiane o północy) daty, żeby nie musieć codziennie wpisywać ręcznie nowej daty do linku.

# In[28]:


import datetime

x = datetime.datetime.now()
yesterday = (int)(x.strftime('%d'))-1
if yesterday > 9:
    date_string = (x.strftime("%m-{}-%Y").format(yesterday))
else:
    date_string = (x.strftime("%m-0{}-%Y").format(yesterday))
print(date_string)


# In[29]:


url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/'
url = url+(date_string)+('.csv')
#url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/06-09-2020.csv'
r = requests.get(url, allow_redirects=True)
open('daily_report.csv', 'wb').write(r.content)
daily = pd.read_csv("daily_report.csv")
daily.tail()


# Dane powyżej są o wiele bardziej szczegółowe (regiony o wiele mniejsze - na przykład poszczególne stany USA i mniejsze obszary w pańśtwach). Dodatkowo zawarte tu są wskaźniki Incidence rate - zachorowalnosć na 100 tyś. mieszkańców oraz Case-Fatality Ratio - czyli stosunek śmierci do wykrytych przypadków.

# Podobne dane znajdziemy pod tym linkiem z European Centre for Disease Prevention and Control: https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-2020-06-09.xlsx

# In[30]:


if yesterday > 9:
    date_string = (x.strftime("%Y-%m-{}").format(yesterday))
else:
    date_string = (x.strftime("%Y-%m-0{}").format(yesterday))
print(date_string)
url = 'https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-'
url = url+(date_string)+('.xlsx')
r = requests.get(url, allow_redirects=True)
open('eu_daily_report.xlsx', 'wb').write(r.content)
eu_daily = pd.read_excel("eu_daily_report.xlsx")
eu_daily.tail()


# Ten plik jest niejako połączeniem tylko dziennych raportów z danymi historycznymi. Zawiera także dane o populacji, co może być przydatne.

# # Wizualizacja dla wybranego regionu/kraju

# Do przeprowadzenia wizualizacji historycznej skorzystałem z pierwszych danych zaprezentowanych w tym Notebooku. Napisałem funkcję, która jako argument przyjmuje wybrany region i rysuje dla niego wykres przypadków, śmierci i wyzdrowień.

# In[31]:


import matplotlib.pyplot as plt
import numpy as np

def draw_historical(region):
    region_data = pd.DataFrame()
    region_data = region_data.append(cases[cases['Country/Region'] == region])
    region_data = region_data.append(deaths[deaths['Country/Region'] == region])
    region_data = region_data.append(recovered[recovered['Country/Region'] == region])
    region_data.reset_index(inplace=True)
    region_data.drop('index', axis = 1, inplace=True)
    region_data["Data type"] = ['Cases', 'Deaths', 'Recovered']
    region_data.set_index("Data type", inplace=True)
    
    fig, ax = plt.subplots()
    fig.set_size_inches(15, 8, forward=True)
    
    tmp = region_data[region_data.index == region_data.index[0]]
    ax.plot(tmp.columns[4:], tmp[tmp.columns[4:]].loc['Cases'], 'b',  label='Cases')
    tmp = region_data[region_data.index == region_data.index[1]]
    ax.plot(tmp.columns[4:], tmp[tmp.columns[4:]].loc['Deaths'], 'r',  label='Deaths')
    tmp = region_data[region_data.index == region_data.index[2]]
    ax.plot(tmp.columns[4:], tmp[tmp.columns[4:]].loc['Recovered'], 'g',  label='Recovered')
    
    ax.set(xlabel='Date', title=('Historyczny wykres dla regionu: ')+region)
    ax.grid()
    plt.xticks(range(0, len(tmp.columns[4:]), 4), tmp.columns[4:][::4], rotation = 45) 
    plt.tight_layout()
    plt.legend()
    plt.show()


# In[38]:


region = 'Poland'
draw_historical(region)


# In[39]:


#Lista regionów do wyboru
cases['Country/Region'].unique()


# # Mapa zachorowań dla Polski

# Tym razem korzystająć z COVID API (ponieważ zawiera nazwy województw) zdecydowałem się narysować mapę zakażeń w Polsce. Współrzędne poprawiłem ręcznie, żeby dobrze wpasowały się na mapę. Wielkość kropki zależy od liczby zachorowań (dzielone przez określoną stałą, w tym wypadku 5).

# In[40]:


url = 'https://api.apify.com/v2/key-value-stores/3Po6TV7wTht4vIEid/records/LATEST?disableRedirect=true'
r = requests.get(url, allow_redirects=True)
data = r.json()
data = data['infectedByRegion']
tmp = [0]*16
for i in range(0, len(data)):
    tmp[i] = data[i]['infectedCount']/5
data


# In[41]:


lat_states = [51.1, 53, 51.2, 52.3, 51.6, 49.8, 52.4, 50.6, 49.85, 53.3, 54.35, 50.3, 50.75, 53.95, 52.4, 53.7]
long_states = [16.3, 18.5, 23, 15.3, 19.5, 20.2, 21.2, 17.8, 22.3, 23, 18.1, 18.95, 20.8, 20.9, 16.9, 15.6]
coords = (14, 24.5, 48.9, 55)
map_image = plt.imread('polska_mapa.png')
fig, ax = plt.subplots(figsize = (20, 20))
ax.scatter(long_states, lat_states, alpha= 0.8, s=tmp, c='r')
ax.set_xlim(coords[0], coords[1])
ax.set_ylim(coords[2], coords[3])
for i in range(0, len(data)):
    ax.annotate(data[i]['infectedCount'], (long_states[i]-0.1, lat_states[i]))
ax.imshow(map_image, extent = coords, aspect= 'equal')


# # Dane globalne

# Postanowiłem także dostać się do danych sumarycznych dla całego świata. W tym celu skorzystałem z danych czasowych - zsumowałem wszystkie wartości śmierci, zachorowań i wyzdrowień (niezależnie od kraju). Następnie wszystkie przerobione dane umieściłem w jednym DataFrame.

# In[42]:


tmp = cases.copy()
tmp.drop(['Province/State', 'Lat', 'Long', 'Country/Region'], axis=1, inplace=True)
global_cases = tmp.sum()

tmp = deaths.copy()
tmp.drop(['Province/State', 'Lat', 'Long', 'Country/Region'], axis=1, inplace=True)
global_deaths = tmp.sum()

tmp = recovered.copy()
tmp.drop(['Province/State', 'Lat', 'Long', 'Country/Region'], axis=1, inplace=True)
global_recovered = tmp.sum()


# In[43]:


global_data = pd.DataFrame (global_cases, columns = ['total_cases'])
global_data.index.names = ['date']
global_data['new_cases'] = 0
global_data['total_deaths'] = global_deaths
global_data['new_deaths'] = 0
global_data['total_recovered'] = global_recovered
global_data['new_recovered'] = 0
for i in range(len(global_data['total_cases'])):
    if i == 0:
        global_data['new_cases'][i] = global_data['total_cases'][i]
        global_data['new_deaths'][i] = global_data['total_deaths'][i]
        global_data['new_recovered'][i] = global_data['total_recovered'][i]
    else:
        global_data['new_cases'][i] = global_data['total_cases'][i]-global_data['total_cases'][i-1]
        global_data['new_deaths'][i] = global_data['total_deaths'][i]-global_data['total_deaths'][i-1]
        global_data['new_recovered'][i] = global_data['total_recovered'][i]-global_data['total_recovered'][i-1]
global_data.tail()


# Na podstawie tych danych można stworzyć analogiczny wykres historyczny, tym razem globalny. Analizując strukturę krzywych można także sprawdzić, czy nastąpiło jej wypłaszczenie.

# In[44]:


def draw_historical_world():

    fig, ax = plt.subplots()
    fig.set_size_inches(15, 8, forward=True)
    
    ax.plot(global_data.index, global_data['total_cases'], 'b',  label='Cases')
    ax.plot(global_data.index, global_data['total_deaths'], 'r',  label='Deaths')
    ax.plot(global_data.index, global_data['total_recovered'], 'g',  label='Recovered')
    
    ax.set(xlabel='Date', title=('Historyczny wykres dla świata'))
    ax.grid()
    plt.xticks(range(0, len(global_data.index), 4), global_data.index[::4], rotation = 45) 
    plt.tight_layout()
    plt.legend()
    plt.show()
           
draw_historical_world()


# # Dzienny rozkład zachorowań i śmierci według kontynentu

# Dane obejmują dzienny raport z European Centre for Disease Prevention and Control. Dane dotyczą tylko jednego dnia - dane całkowite przedstawiam niżej. Zamieniłem także kolejnością kontynenty, aby lepiej wyklądały na wykresie.

# In[45]:


tmp = eu_daily[eu_daily['dateRep']=='2020-06-09']
tmp = tmp.groupby('continentExp')['cases', 'deaths'].sum().reset_index()
b, c = tmp.iloc[0].copy(), tmp.iloc[1].copy()
tmp.iloc[0], tmp.iloc[1] = c,b
b, c = tmp.iloc[3].copy(), tmp.iloc[4].copy()
tmp.iloc[3], tmp.iloc[4] = c,b
tmp


# In[46]:


import matplotlib
matplotlib.rcParams['font.size'] = 13.0
fig, axs = plt.subplots(1, 2, figsize = (15, 10))
axs[0].pie(tmp['cases'], labels = tmp['continentExp'], autopct=lambda p: '{:.2f}%({:.0f})'.format(p,(p/100)*tmp['cases'].sum()))
axs[0].set_title('Dzienny rozkład zachorowań')
axs[1].pie(tmp['deaths'], labels = tmp['continentExp'], autopct=lambda p: '{:.2f}%({:.0f})'.format(p,(p/100)*tmp['deaths'].sum()))
axs[1].set_title('Dzienny rozkład śmierci')
plt.show()


# # Całkowity historyczny rozkład zachorowań i śmierci według kontynentu

# Wykresy są tworzone w ten sam sposób, jedynie należało zsumować poszczególne wartości.

# In[47]:


tmp = eu_daily.copy()
tmp = tmp.groupby('continentExp')['cases', 'deaths'].sum().reset_index()
b, c = tmp.iloc[0].copy(), tmp.iloc[1].copy()
tmp.iloc[0], tmp.iloc[1] = c,b
b, c = tmp.iloc[3].copy(), tmp.iloc[4].copy()
tmp.iloc[3], tmp.iloc[4] = c,b
tmp


# In[48]:


fig, axs = plt.subplots(1, 2, figsize = (15, 10))
axs[0].pie(tmp['cases'], labels = tmp['continentExp'],
           autopct=lambda p: '{:.2f}%({:.0f})'.format(p,(p/100)*tmp['cases'].sum()))
axs[0].set_title('Całkowity rozkład zachorowań')
axs[1].pie(tmp['deaths'], labels = tmp['continentExp'],
           autopct=lambda p: '{:.2f}%({:.0f})'.format(p,(p/100)*tmp['deaths'].sum()))
axs[1].set_title('Całkowity rozkład śmierci')
plt.show()


# Co warto zauważyć - Europa odpowiada za około 30% wszystkich zachorowań na świecie i aż za ~44% globalnych śmierci. W Azji natomiast jest odwrotnie - około 20% zachorowań globalnych, a tylko ~9% globalnych śmierci. 

# # Historyczna mapa zachorowań dziennych na świecie

# Poniżej zwizualizowałem codzienne przypadki zachorowań na świecie. Nie wybrałem sumarycznych zachorowań, ponieważ kropki ciągle by rosły i mapa byłaby nieczytelna. Co prawda przeważająca ilość zachorowań z krajów takich jak USA nadal źle wpływa na odbiór wizualny wykresu, jednak jest to opcja bardziej czytelna.

# In[103]:


cases_new = cases.copy()
for i in range(4, len(cases_new.columns)-1):
    cases_new[cases_new.columns[i]] = cases_new[cases_new.columns[i+1]]-cases_new[cases_new.columns[i]]
    for j in range(len(cases_new[cases_new.columns[i]])):
        if cases_new[cases_new.columns[i]][j] < 0:
            cases_new[cases_new.columns[i]][j] = 0
cases_new = cases_new.drop(['6/9/20'], axis=1)
cases_new.head()


# In[108]:


sadsad = (cases_new[cases_new.columns[4:][i]]/200)
sadsad = [1000 if x > 1000 else x for x in sadsad]
print(sadsad)


# In[113]:


import plotly.graph_objects as go

frames = []
for i in range(len(cases_new.columns[4:])):
    limit = (cases_new[cases_new.columns[4:][i]]/150)
    limit = [100 if x > 100 else x for x in limit]
    #max size 100 otherwise hard to read
    marker = dict(size=limit)
    frames.append(go.Frame(data = go.Scattergeo(lon = cases_new['Long'], lat = cases_new['Lat'], marker = marker)))
       
fig = go.Figure(
    data = go.Scattergeo(),
    layout=go.Layout(title="Zachorowania na świecie", geo = dict(scope='world'), updatemenus=[
        dict(type="buttons", buttons=[dict(label="Play", method="animate", args=[None])])]),
    frames = frames)
fig.show()


# In[ ]:


duzo zrodel - wrzucac tyle, ile sie uda
informacje dzienne
zbadac zrodla - czy nie takie same - pochodzenie danych


# In[ ]:


wizualizacja - sposoby

