# To add a new cell, type '#%%'
# To add a new markdown cell, type '#%% [markdown]'
#%%
import pandas as pd
import numpy as np
import networkx as nx
import holoviews as hv
from holoviews import opts
import warnings
warnings.filterwarnings('ignore') # silence annoying warnings

#%% [markdown]
# ## Bring in data

#%%
df = pd.read_csv("sandbox_data.csv")
df.drop(['Action'], axis=1, inplace=True)

#%% [markdown]
# ## Convert data into edgelist

#%%
def _connect_on(df, attr):
    """
    df (pd.DataFrame): data
    attr (string): data column to use as edge connector
    
    Returns pandas dataframe with edgelist and attributes
    """
    el = df.merge(
        right=df[['ID', attr]], 
        left_on=attr, 
        right_on=attr, 
        how='inner'
        )

    # Remove rows where ID_x and ID_y are equal
    el = el.query("ID_x != ID_y")

    # Remove rows where (ID_x, ID_y) = (ID_y, ID_x)
    m = pd.DataFrame(np.sort(el[['ID_x', 'ID_y']], axis=1)).duplicated()
    el = el.loc[~m.values]

    # Sort and arrange for igraph
    el = el[["ID_x", "ID_y", "ActionType", "Sector", "Hazard", "Strategy", "Term"]]
    return el

#%% [markdown]
# ## Create networkx graph

#%%
def create_graph(df, attr):
    """
    df (pd.DataFrame): data
    attr (string): data column to use as edge connector
    
    Returns networkx graph with node and edge attributes
    """
    el = _connect_on(df, attr)
    g = nx.from_pandas_edgelist(el, 'ID_x', 'ID_y', [attr])
    
    # add node attributes
    for a in df.drop(['ID'], axis=1).columns:
        nx.set_node_attributes(g, name=a, values=dict(zip(df.ID, df[a])))
    return g


#%%
g = create_graph(df, 'Strategy')

#%% [markdown]
# ## Set viz defaults

#%%
hv.extension('bokeh')
defaults = dict(
    width=600, 
    height=600, 
    padding=0.1, 
    xaxis=None, 
    yaxis=None, 
    show_frame=False,
)
hv.opts.defaults(
    opts.EdgePaths(**defaults), 
    opts.Graph(**defaults), 
    opts.Nodes(**defaults),
)

#%% [markdown]
# ## Plot

#%%
graph_dict = {
    (attr, i/10.): hv.Graph.from_networkx(create_graph(df, attr), 
                                          nx.spring_layout, k=i/10., seed=9) 
    for attr in df.drop(['ID'], axis=1).columns 
    for i in range(1,10,1)
}


#%%
holomap = hv.HoloMap(graph_dict, kdims=['Connection', 'k_param'])
holomap.opts(cmap='Accent', node_color='Term')


#%%



