# module import
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# global parameters
colours = ['#006183', '#7AB538', '#FF3000', '#FFD800', '#00C930', '#00838F', '#FF6A00', '#FF9A24', 'grey']
weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', '0']
plt.style.use('fivethirtyeight')

# data gathering
df = pd.read_excel('https://github.com/rikunert/bike_rentals/raw/master/Bike-sharing_sample.xlsx',
                   skiprows=range(4))
df.head()

# data cleaning
df.fillna(value=0, inplace=True)

# data types
df.loc[:, 'Date'] = pd.to_datetime(df.loc[:, 'Date'], errors='coerce')
df = df.set_index('Date')

# visualisation

#overall proportion plot
prop_total = df.loc[:, 'Deezer': 'non-App'].sum()/df.loc[:, 'Deezer': 'non-App'].sum().sum() * 100
prop_total = pd.DataFrame({'market_share':prop_total,
                           'colours':colours})
prop_total.sort_values('market_share', inplace=True, ascending=False)
fig_total, ax = plt.subplots(figsize=[8, 6])
prop_total.loc[:, 'market_share'].plot(kind='bar', ax=ax, color=prop_total.loc[:, 'colours'])
ax.set(ylabel='Market share (May and June 2018)', title='Rental bike market in Berlin')
# yticks
ax.set_yticks(range(0, 40, 10))
fmt = '%.0f%%' # Format you want the ticks, e.g. '40%'
yticks = mtick.FormatStrFormatter(fmt)
ax.yaxis.set_major_formatter(yticks)
ax.grid(visible=False, axis='x')
ax.text(0.8, 0.8, 'N = {}'.format(int(df.loc[:, 'Deezer': 'non-App'].sum().sum())),
        horizontalalignment='right',
        transform=ax.transAxes)
fig_total.text(0.99, 0.01, '@rikunert', color='grey', style='italic',
         horizontalalignment='right')
plt.tight_layout()
fig_total.savefig('rental_shares_total.png')


def prop_plotter(df_count, df_prop):

    fig, ax = plt.subplots(tight_layout=True, figsize=[10, 6])

    df_prop.plot(ax=ax, color=colours, legend=False,
                 marker='.', markersize=20,
                 linewidth=3)

    #x ticks
    if df_prop.index.dtype == 'int64' or df_prop.index.dtype == '<M8[ns]':  # KW
        ax.set_xticks(df_prop.index)

    labels = [item.get_text() for item in ax.get_xticklabels()]
    print(labels)
    for i in range(df_prop.shape[0]):
        if df_prop.index.dtype == 'int64':  # KW
            labels[i] = 'N={}\n\n{}'.format(int(df_count.loc[df_count.index[i], 'sum']),
                                            int(df_prop.index[i]))
        elif df_prop.index.dtype == 'str':  # weekdays
            labels[i + 1] = 'N={}\n\n{}'.format(int(df_count.loc[df_count.index[i], 'sum']),
                                            df_prop.index[i])

    ax.set_xticklabels(labels)

    # yticks
    ax.set_yticks(range(0, 50, 10))
    fmt = '%.0f%%' # Format you want the ticks, e.g. '40%'
    yticks = mtick.FormatStrFormatter(fmt)
    ax.yaxis.set_major_formatter(yticks)

    ax.set(ylabel='rental bike market share in Berlin',
           title=' ')

    # new legend
    if df_prop.index.dtype == 'int64':
        x_pos = ax.get_xticks()
    else:
        x_pos = ax.get_xticks()[1:-1]
    if df_prop.index.dtype == '<M8[ns]':
        x_adjustment = len(x_pos)/30
    else:
        x_adjustment = len(x_pos) / 50
    for i, brand in enumerate(df_prop.columns):
        print(brand)
        ax.text(x=x_pos[-1] + x_adjustment,
                y=df_prop.loc[df_prop.index[-1], brand],
                s=brand,
                color=colours[i],
                verticalalignment='center')

    ax.margins(0.15, 0.05)
    ax.grid(visible=False, axis='x')

    #author line
    fig.text(0.99, 0.01, '@rikunert', color='grey', style='italic',
                     horizontalalignment='right')

    return fig, ax

# calendar week analysis
df_KW1 = df.resample("7d").sum().loc[:, 'Deezer':'sum']
df_KW1.index = df_KW1.index.week
df_KW1.index.name = 'calendar week'

df_KW1_prop = df_KW1.div(df_KW1['sum'], axis=0).loc[:, :'non-App'] * 100

fig_KW, ax_KW = prop_plotter(df_KW1, df_KW1_prop)
ax_KW.set(title='The rise and fall of Ofo')

# weekday analysis
df_d = df.copy()
df_d.index = pd.Series(weekdays)[df_d.index.weekday]
df_day1 = df_d.groupby(df_d.index).sum().loc[:, 'Deezer':'sum']
df_day1.index.name = 'week day'

df_day1_prop = df_day1.div(df_day1['sum'], axis=0).loc[:, :'non-App']

df_day1 = df_day1.reindex(weekdays[:-1])
df_day1_prop = df_day1_prop.reindex(weekdays[:-1]) * 100

fig_day, ax_day = prop_plotter(df_day1, df_day1_prop)
ax_day.set(title='Intra-week differences in bike rental market share')
fig_day.savefig('rental_shares_day.png')

# rolling average analysis
df_D = df.resample("D").sum().loc[:, 'Deezer':'sum']
df_rolling = df_D.rolling(7, min_periods=4, center=True).sum()
df_rolling_prop = df_rolling.div(df_rolling['sum'], axis=0).loc[:, :'non-App'] * 100

fig_rolling, ax_rolling = prop_plotter(df_rolling, df_rolling_prop)
ax_rolling.set(title='A volatile bike rental market')
ax_rolling.set(ylabel='rental bike market share in Berlin \n(7 day rolling average)',
               xlabel='May                                                  June\n2018')
fig_rolling.savefig('rental_shares_rolling.png')

# cost analysis
duration = 120
df_cost = pd.DataFrame(data={'Deezer': [(i//30 + 1) * 1.5 for i in range(duration)],
                        'Lidl':[(i//30 + 1) * 1.5 for i in range(30)] + [((i//30 + 1) * 1) + 0.5 for i in range(30, duration)],
                        'Mo-Bike':[(i//20 + 1) * 0.5 for i in range(duration)],
                        'Ofo':[(i//30 + 1) * 0.8 for i in range(duration)],
                        'Lime-E':[(i//1 + 1) * 0.15 + 1 for i in range(duration)],
                        'Byke':[(i//30 + 1) * 0.5 for i in range(duration)],
                        'Donkey':[(i//30 + 1) * 1.25 for i in range(duration)],
                        'O-Bike':[(i//30 + 1) * 1 for i in range(duration)]})
df_cost = df_cost[df.columns[5:-2]]#  reorder columns
df_cost_extra = df_cost.copy()
df_cost_extra['Lidl'] = df_cost_extra['Lidl'] + 3
df_cost_extra['Mo-Bike'] = df_cost_extra['Mo-Bike'] + 2
df_cost_extra['O-Bike'] = df_cost_extra['O-Bike'] + 79

def cost_plotter(df):

    fig_cost, ax_cost = plt.subplots(tight_layout=True, figsize=[10, 6])
    df.plot(drawstyle="steps-post", linewidth=4, color=colours,
             ax=ax_cost,
             legend=False)
    ax_cost.set(xlabel='Rental duration (minutes)',
       ylabel='Cost without deposit or subscription (EUR)',
       ylim=[0, 8],
       title='Price differences between rental bikes in Berlin')
    ax_cost.grid(visible=False, axis='x')

    # additional plotting with different line styles
    lstyle = [':', ':', ':',
                 '-', '-', '-',
                 ':', '-', '-']
    for i in [1, 2, 0]:
        df.iloc[:, i].plot(drawstyle="steps-post",
                    linewidth=4, color=colours[i],
                    linestyle=lstyle[i],
            ax=ax_cost,
            legend=False)

    # new legend
    x_pos = ax_cost.get_xticks()
    x_adjustment = len(x_pos)/5
    for i, brand in enumerate(df_cost.columns):
        if (brand == 'Lime-E') and (df.max().max() == df['Lime-E'].max()):
            ax_cost.text(x=x_pos[-2] + x_adjustment,
                y=max(ax_cost.get_yticks()),
                s=brand,
                color=colours[i],
                verticalalignment='center')
        else:
            ax_cost.text(x=x_pos[-2] + x_adjustment,
                y=df.loc[df.index[-1], brand],
                s=brand,
                color=colours[i],
                verticalalignment='center')

    ax_cost.margins(0.15, 0.05)
    ax_cost.grid(visible=False, axis=1)

    fig_cost.text(0.99, 0.01, '@rikunert', color='grey', style='italic',
                     horizontalalignment='right')
    return fig_cost, ax_cost

fig_cost, ax_cost = cost_plotter(df_cost)
fig_cost.savefig('rental_costs.png')

fig_cost_extra, ax_cost_extra = cost_plotter(df_cost_extra)
ax_cost_extra.set(ylabel='Cost including deposit or subscription (EUR)',
                  ylim=[0, 90],
                  title='Price differences between rental bikes including set-up costs')
fig_cost_extra.savefig('rental_costs_extra.png')