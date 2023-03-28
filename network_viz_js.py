# -*- coding: utf-8 -*-
"""Network Viz.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1V02VdY7OvR87miM_B9GtD320cy_hRfdP

https://programminghistorian.org/en/lessons/exploring-and-analyzing-network-data-with-python

#Import Libraries
"""

# !pip install pyvis
# !pip install Network
# !pip install TapTool

import pandas as pd
import networkx
# !pip install bokeh
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from operator import itemgetter
# from bokeh.io import output_notebook, show, save
from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine, Toggle, PointDrawTool, Tooltip
from bokeh.plotting import figure, curdoc, from_networkx
from bokeh.models import EdgesAndLinkedNodes, NodesAndLinkedEdges, LabelSet
from bokeh.palettes import Blues8, Spectral8
from bokeh.transform import linear_cmap
from networkx.algorithms import community
"""#Data Loading"""

df = pd.read_csv("/Users/wanxing/PycharmProjects/PennEcosystem/bokeh-app/data/network.csv")
print("reading data")
df.rename(columns={'domains_clean':'source', 'embedded_domains':'target', 'embedded_domains.1':'count'}, inplace=True)
start = 1
end = 10
width = end - start
df['weight'] =(df['count']-df['count'].min())/(df['count'].max()-df['count'].min())*width+start
df = df[df['target']!='None']
df['source_truncated'] = df['source'].apply(lambda x: x.replace('.upenn.edu',''))
df['target_truncated'] = df['target'].apply(lambda x: x.replace('.upenn.edu',''))

df_cat = pd.read_excel("/Users/wanxing/PycharmProjects/PennEcosystem/bokeh-app/data/site_domainV2.xlsx", sheet_name='domain')
df_cat['Category'] = df_cat[['R&D','Teaching','Organizer', 'Knowledge', 'Media']].apply(lambda x: ','.join(x[x.isnull()==False].index), axis=1)
df_cat['domain_truncated'] = df_cat['domain'].apply(lambda x: x.split('/')[2].replace('www.','').replace('.upenn.edu',''))

url_class = dict(zip(df_cat['Node_Name'],df_cat['domain']))
category_class = dict(zip(df_cat['Node_Name'],df_cat['Category']))
index_class = dict(zip(df_cat['domain_truncated'],df_cat['Node_Name']))
name_class = dict(zip(df_cat['Node_Name'],df_cat['Popup_Name']))


df['source_name'] = df['source_truncated'].map(index_class)
df['target_name'] = df['target_truncated'].map(index_class)
df['source_category'] = df['source_name'].map(category_class)
df['target_category'] = df['target_name'].map(category_class)

target_domains_sorted = sorted(df['target_truncated'].map(index_class).unique())
source_domains_sorted = sorted(df['source_truncated'].map(index_class).unique())
print(df)

domains_sorted = sorted(df[df['source_category'].str.contains('Teaching')==False]['source_name'].unique())
"""#Network(interactive)"""
from bokeh.core.enums import SizingMode
from bokeh.io import show
from bokeh.models import CustomJS, MultiChoice
from bokeh.io.output import output_file
from bokeh.models import Button, CustomJS, Div, CheckboxButtonGroup, TapTool, OpenURL, Select
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models import CDSView, ColumnDataSource, GroupFilter
from bokeh.io import show
from networkx.algorithms import community

#Choose colors for node and edge highlighting
node_highlight_color = '#2171b5'
node_fill_color = '#4292c6'
edge_highlight_color = '#d53e4f'

#Choose attributes from G network to size and color by — setting manual size (e.g. 10) or color (e.g. 'skyblue') also allowed
size_by_this_attribute = 'adjusted_node_size'
# color_by_this_attribute = 'modularity_color'

#Pick a color palette — Blues8, Reds8, Purples8, Oranges8, Viridis8
# color_palette = Blues8

#Establish which categories will appear when hovering over each node
HOVER_TOOLTIPS = [
    ("Name", "@Name"),
    ("Number of ties", "@degree"),
    ("URL", "@URL"),
    ("Category", "@category")
]

#Create a plot — set dimensions, toolbar, and title
plot = figure(tooltips = HOVER_TOOLTIPS,
              tools="pan,wheel_zoom,save,reset,tap", active_scroll='wheel_zoom',
              x_range=Range1d(-15.1, 15.1), y_range=Range1d(-15.1, 15.1), 
              plot_width=1000)

plot.xgrid.grid_line_color = None
plot.ygrid.grid_line_color = None
plot.axis.visible=False
labels = ["R&D", "Teaching", "Organizer", "Knowledge", "Media"]


def callback_generate():
    new_plot = figure(tooltips = HOVER_TOOLTIPS,
              tools="pan,wheel_zoom,save,reset,tap", active_scroll='wheel_zoom',
              x_range=Range1d(-15.1, 15.1), y_range=Range1d(-15.1, 15.1), 
              plot_width=1000)
    
    new_plot.xgrid.grid_line_color = None
    new_plot.ygrid.grid_line_color = None
    new_plot.axis.visible=False
    
    if len(source_checkbox_button_group.active) == 0 and len(target_checkbox_button_group.active) > 0:
        source_group_selected = ["R&D", "Teaching", "Organizer", "Knowledge", "Media"]
    else:
        source_group_selected = [source_checkbox_button_group.labels[i] for i in source_checkbox_button_group.active]
    if len(target_checkbox_button_group.active) == 0 and len(source_checkbox_button_group.active) > 0:
        target_group_selected = ["R&D", "Teaching", "Organizer", "Knowledge", "Media"]
    else:
        target_group_selected = [target_checkbox_button_group.labels[i] for i in target_checkbox_button_group.active]

    source_node_selected = source_multi_choice.value
    target_node_selected = target_multi_choice.value
    if (len(source_node_selected)==0 & len(target_node_selected)==0 & len(source_checkbox_button_group.active)==0 & len(target_checkbox_button_group.active)==0):
        source = df
    else:
        source =  df[(df["target_category"].isin(target_group_selected)) & (df['source_category'].isin(source_group_selected)) | 
                 (df["source_name"].isin(source_node_selected)) | (df['target_name'].isin(target_node_selected))]
    print(source)
    if remove_school_button.active:
        df_filtered =  source[(source["target_category"].str.contains('Teaching')==False) & (source['source_category'].str.contains('Teaching')==False)]
        # df_filtered = d[d['source_category'].str.contains(cat_selected)==False]
        print("updated",df_filtered)
    else:
        df_filtered = source
    print(df_filtered)
    G_generate = networkx.from_pandas_edgelist(df_filtered, 'source_name', 'target_name', edge_attr=['weight'], create_using=networkx.DiGraph())

    #Calculate degree for each node and add as node attribute
    degrees = dict(networkx.degree(G_generate))
    networkx.set_node_attributes(G_generate, name='degree', values=degrees)

    # #Slightly adjust degree so that the nodes with very small degrees are still visible
    number_to_adjust_by = 5
    adjusted_node_size = dict([(node, degree+number_to_adjust_by) for node, degree in networkx.degree(G)])
    networkx.set_node_attributes(G_generate, name='adjusted_node_size', values=adjusted_node_size)
    networkx.set_node_attributes(G_generate, url_class, "URL")
    networkx.set_node_attributes(G_generate, category_class, "category")
    networkx.set_node_attributes(G_generate, name_class, "Name")
    # Configure tap tool
    taptool = new_plot.select(type=TapTool)
    taptool.callback = OpenURL(url="@URL")
    network_graph = from_networkx(G_generate, pos, scale=15, center=(0, 0))
    #Create newnetwork graph from filtered data
    #Set node sizes and colors according to node degree (color as category from attribute)
    network_graph.node_renderer.glyph = Circle(size=size_by_this_attribute, fill_color=node_fill_color)
    #Set node highlight colors
    network_graph.node_renderer.hover_glyph = Circle(size=size_by_this_attribute, fill_color=node_highlight_color, line_width=2)
    network_graph.node_renderer.selection_glyph = Circle(size=size_by_this_attribute, fill_color=node_highlight_color, line_width=2)
    #Set edge opacity and width
    network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.3, line_width=1)
    #Set edge highlight colors
    network_graph.edge_renderer.selection_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)
    network_graph.edge_renderer.hover_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)
    #Highlight nodes and edges
    network_graph.selection_policy = NodesAndLinkedEdges()
    network_graph.inspection_policy = NodesAndLinkedEdges()
    new_plot.renderers.append(network_graph)
    #Add Labels
    x, y = zip(*network_graph.layout_provider.graph_layout.values())
    print(x,y)
    node_labels = list(G.nodes())
    label_source = ColumnDataSource({'x': x, 'y': y, 'name': node_labels})
    labels = LabelSet(x='x', y='y', text='name', source=label_source, background_fill_color='white', text_font_size='10px', background_fill_alpha=.8)
    new_plot.renderers.append(labels)
    group = row(column(source_cat_txt, source_multi_choice, source_checkbox_button_group),
                column(target_cat_txt, target_multi_choice, target_checkbox_button_group),
                sizing_mode='stretch_both')
    layout.children[2] = new_plot
    # update metrics
    new_density = Div(text="{:.2f}".format(networkx.density(G_generate)))
    new_clustering = Div(text="{:.2f}".format(networkx.average_clustering(G_generate)))
    degree = networkx.degree_centrality(G_generate)
    in_degree = networkx.in_degree_centrality(G_generate)
    out_degree = networkx.out_degree_centrality(G_generate)
    eigen_degree = networkx.eigenvector_centrality_numpy(G_generate)

    sorted_degree = sorted(degree.items(), key=itemgetter(1), reverse=True)
    sorted_in_degree = sorted(in_degree.items(), key=itemgetter(1), reverse=True)
    sorted_out_degree = sorted(out_degree.items(), key=itemgetter(1), reverse=True)
    sorted_eigen_degree = sorted(eigen_degree.items(), key=itemgetter(1), reverse=True)

    in_degree_output = " "
    for n, v in sorted_in_degree[:5]:
        in_degree_output += n + " " + "{:.2f}".format(v) + '</br>'
    new_in_degree_output_div = Div(text=str(in_degree_output))
    out_degree_output = " "
    for n, v in sorted_out_degree[:5]:
        out_degree_output += n + " " + "{:.2f}".format(v) + '</br>'
    new_out_degree_output_div = Div(text=str(out_degree_output))
    eigen_degree_output = " "
    for n, v in sorted_eigen_degree[:5]:
        eigen_degree_output += n + " " + "{:.2f}".format(v) + '</br>'
    new_eigen_degree_output_div = Div(text=str(eigen_degree_output))
    analysis.children[4] = new_density
    analysis.children[6] =  new_clustering
    analysis.children[8] = new_in_degree_output_div
    analysis.children[10] = new_out_degree_output_div
    analysis.children[12] = new_eigen_degree_output_div


## Source
source_node_txt = Div(text="Select Source Node(s):")
source_checkbox_button_group = CheckboxButtonGroup(labels=labels)
source_cat_txt = Div(text="Select Source Group(s):")
source_multi_choice = MultiChoice(options=source_domains_sorted)
# source_multi_choice.js_on_change("value", CustomJS(code="""
#     console.log('multi_choice: value=' + this.value, this.toString())
# """))
# source_RD = df[df["source_category"].str.contains("R&D")==True]
# source_Teaching = df[df["source_category"].str.contains("Teaching")==True]
# source_Organizer = df[df["source_category"].str.contains("Organizer")==True]
# source_Knowledge = df[df["source_category"].str.contains("Knowledge")==True]
# source_Media = df[df["source_category"].str.contains("Media")==True]
# G1 = networkx.from_pandas_edgelist(source_RD, 'source', 'target', edge_attr=['weight'], create_using=nx.DiGraph())
# G2 = networkx.from_pandas_edgelist(source_Teaching, 'source', 'target', edge_attr=['weight'], create_using=nx.DiGraph())
# G3 = networkx.from_pandas_edgelist(source_Organizer, 'source', 'target', edge_attr=['weight'], create_using=nx.DiGraph())
# G4 = networkx.from_pandas_edgelist(source_Knowledge, 'source', 'target', edge_attr=['weight'], create_using=nx.DiGraph())
# G5 = networkx.from_pandas_edgelist(source_Media, 'source', 'target', edge_attr=['weight'], create_using=nx.DiGraph())
# selected_nodes = [n for n,v in G.nodes(data=True) if v['since'] == 'December 2008']  
# args = [('checkbox_source', source_checkbox_button_group)]
# code = "var active = cb_obj.active;"
# for c in range(len(LABELS)):
#     network = networkx.from_pandas_edgelist(G, 'source', 'target', edge_attr=['weight'], create_using=nx.DiGraph())
#     line = p.line(x='dates', y=currencies[c], line_width=2, alpha=1, name=currencies[c], legend_label=currencies[c], source=source)
#     args += [('line'+str(c), line)]
#     code += "line{}.visible = active.includes({});".format(c, c)


G = networkx.from_pandas_edgelist(df, 'source_name', 'target_name', edge_attr=['weight'], create_using=networkx.DiGraph())
# callback = CustomJS(args = {'checkbox':source_checkbox_button_group, 'df': df, 'data_new': data_new},
# code = """
# # console.log(df);
# var data = df.data;
# var s_data = data_new.data;
# var source_category = data['source_category'];
# var select_vals = cb_obj.active.map(x => cb_obj.labels[x]);
# console.log(select_vals);
# var x_data = data['source'];
# var y_data = data['target'];
# var x = s_data['source'];
# x.length = 0;
# var y = s_data['target'];
# y.length = 0;
# for (var i = 0; i < x_data.length; i++) {
#     if (select_vals.indexOf(source_category[i]) >= 0) {
#         x.push(x_data[i]);
#         y.push(y_data[i]);
#         }
# }
# data_new.change.emit();
# # """)
# def update(event):
# #Callback    
#     print("update triggered")
#     df.data = data
#     # create a callback that will reset the datasource

## Target
target_node_txt = Div(text="Select Target Node(s):")
target_checkbox_button_group = CheckboxButtonGroup(labels=labels)
target_cat_txt = Div(text="Select Target Group(s):")
target_multi_choice = MultiChoice(options=target_domains_sorted)
# target_multi_choice.js_on_change("value", CustomJS(code="""
#     console.log('multi_choice: value=' + this.value, this.toString())
# """))


#Calculate degree for each node and add as node attribute
degrees = dict(networkx.degree(G))
networkx.set_node_attributes(G, name='degree', values=degrees)

# #Slightly adjust degree so that the nodes with very small degrees are still visible
number_to_adjust_by = 5
adjusted_node_size = dict([(node, degree+number_to_adjust_by) for node, degree in networkx.degree(G)])
networkx.set_node_attributes(G, name='adjusted_node_size', values=adjusted_node_size)

# communities = community.greedy_modularity_communities(G)
#Add modularity class and color as attributes to network graph

# # Create empty dictionaries
# modularity_class = {}
# modularity_color = {}
# #Loop through each community in the network
# for community_number, community in enumerate(communities):
#     #For each member of the community, add their community number and a distinct color
#     for name in community: 
#         modularity_class[name] = community_number
#         modularity_color[name] = Spectral8[community_number]

# Add modularity class, color, URLs, categoty, degree centrality as attributes from the network above
# networkx.set_node_attributes(G, modularity_class, 'modularity_class')
# networkx.set_node_attributes(G, modularity_color, 'modularity_color')
networkx.set_node_attributes(G, url_class, "URL")
networkx.set_node_attributes(G, category_class, "category")
networkx.set_node_attributes(G, name_class, "Name")
# Configure tap tool
taptool = plot.select(type=TapTool)
taptool.callback = OpenURL(url="@URL")
# plot the network using spiral layout, other options:https://networkx.org/documentation/stable/reference/drawing.html#module-networkx.drawing.layout
pos = networkx.spring_layout(G,scale=13, k=0.95)
network_graph = from_networkx(G, pos, center=(0, 0))
network_graph.edge_renderer.data_source.data["line_width"] = [G.get_edge_data(a,b)['weight'] for a, b in G.edges()]
#Create newnetwork graph from filtered data
#Set node sizes and colors according to node degree (color as category from attribute)
network_graph.node_renderer.glyph = Circle(size=size_by_this_attribute, fill_color = node_fill_color)
#Set node highlight colors
network_graph.node_renderer.hover_glyph = Circle(size=size_by_this_attribute, fill_color=node_highlight_color, line_width='line_width')
network_graph.node_renderer.selection_glyph = Circle(size=size_by_this_attribute, fill_color=node_highlight_color, line_width='line_width')

#Set edge opacity and width
network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.3, line_width='line_width')
#Set edge highlight colors
network_graph.edge_renderer.selection_glyph = MultiLine(line_color=edge_highlight_color, line_width='line_width')
network_graph.edge_renderer.hover_glyph = MultiLine(line_color=edge_highlight_color, line_width='line_width')

#Highlight nodes and edges
network_graph.selection_policy = NodesAndLinkedEdges()
network_graph.inspection_policy = NodesAndLinkedEdges()

plot.renderers.append(network_graph)


#Add Labels
x, y = zip(*network_graph.layout_provider.graph_layout.values())
node_labels = list(G.nodes())
label_source = ColumnDataSource({'x': x, 'y': y, 'name': node_labels})
labels = LabelSet(x='x', y='y', text='name', source=label_source, background_fill_color='white', text_font_size='10px', background_fill_alpha=.8)
plot.renderers.append(labels)

draw_tool = PointDrawTool(renderers=[network_graph.node_renderer])
plot.add_tools(draw_tool)
plot.toolbar.active_tap = draw_tool

#Dropdown widget
#User can select a single node and see all the nodes it connects to (regardless of source or target), and updated metrics.
menu = list(zip(domains_sorted, domains_sorted))

selection = Select(options=["Full Network"]+menu)
egocentric_text = Div(text="Learn more about an individual node:")

def callback_select(attr, old, new):
    # selected_node=selection.value
    # print(selected_node)
    # source_list = [n for n, nbrdict in G.adjacency() if len(nbrdict) > 0]
    # if selected_node not in source_list:
    #     shortest = networkx.shortest_path(G.to_undirected(),target=selected_node)
    # shortest = networkx.shortest_path(G.to_undirected(),source=selected_node)
    # filtered = [k for k,v in shortest.items() if len(v)==2 or len(v)==1]
    # def filter_node(n):
    #     return n in filtered
    # def filter_edge(n1, n2):
    #     return n1 in source or n2 in source
    # node_data =network_graph.node_renderer.data_source.data
    # new_node_data = {k: [x for i, x in enumerate(v) if node_data['index'][i] in filtered] for k, v in node_data.items()}
    # network_graph.node_renderer.data_source.data = new_node_data
    # # network_graph.edge_renderer.data_source.data = 
    # # G_node = networkx.subgraph_view(G, filter_node=filter_node, filter_edge=filter_edge)
    # # network_graph=networkx.draw_networkx(G_node, pos=pos)
    # # network_graph = from_networkx(G_node, networkx.spring_layout, scale=15, center=(0, 0))
    # #Create newnetwork graph from filtered data
    # #Set node sizes and colors according to node degree (color as category from attribute)
    new_plot = figure(tooltips = HOVER_TOOLTIPS,
              tools="pan,wheel_zoom,save,reset,tap", active_scroll='wheel_zoom',
              x_range=Range1d(-15.1, 15.1), y_range=Range1d(-15.1, 15.1), 
              plot_width=1000)
    selected_node=selection.value
    print("node", selected_node)

    new_G = networkx.ego_graph(G, selected_node)
    # new_G = networkx.from_pandas_edgelist(source, 'source', 'target', edge_attr=['weight'], create_using=networkx.DiGraph())

    #Calculate degree for each node and add as node attribute
    degrees = dict(networkx.degree(new_G))
    networkx.set_node_attributes(new_G, name='degree', values=degrees)

    #Slightly adjust degree so that the nodes with very small degrees are still visible
    number_to_adjust_by = 5
    adjusted_node_size = dict([(node, degree+number_to_adjust_by) for node, degree in networkx.degree(new_G)])
    networkx.set_node_attributes(new_G, name='adjusted_node_size', values=adjusted_node_size)

    # networkx.set_node_attributes(new_G, url_class, "URL")
    # networkx.set_node_attributes(new_G, category_class, "category")
    # # Configure tap tool
    # taptool = new_plot.select(type=TapTool)
    # taptool.callback = OpenURL(url="@URL")
    new_network_graph = from_networkx(new_G, networkx.spring_layout, scale=15, center=(0, 0))
    #Create newnetwork graph from filtered data
    #Set node sizes and colors according to node degree (color as category from attribute)
    new_network_graph.node_renderer.glyph = Circle(size=size_by_this_attribute, fill_color=node_fill_color)
    #Set node highlight colors
    new_network_graph.node_renderer.hover_glyph = Circle(size=size_by_this_attribute, fill_color=node_highlight_color, line_width=2)
    new_network_graph.node_renderer.selection_glyph = Circle(size=size_by_this_attribute, fill_color=node_highlight_color, line_width=2)
    #Set edge opacity and width
    new_network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.3, line_width=1)


    #Set edge highlight colors
    new_network_graph.edge_renderer.selection_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)
    new_network_graph.edge_renderer.hover_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)
    #Highlight nodes and edges
    new_network_graph.selection_policy = NodesAndLinkedEdges()
    new_network_graph.inspection_policy = NodesAndLinkedEdges()
    new_plot.renderers.append(new_network_graph)
    #Add Labels
    x, y = zip(*new_network_graph.layout_provider.graph_layout.values())
    node_labels = list(new_G.nodes())
    label_source = ColumnDataSource({'x': x, 'y': y, 'name': node_labels})
    labels = LabelSet(x='x', y='y', text='name', source=label_source, background_fill_color='white', text_font_size='10px', background_fill_alpha=.8)
    new_plot.renderers.append(labels)

    layout.children[2] = new_plot
    # # update metrics
    new_density = Div(text="{:.2f}".format(networkx.density(new_G)))

    in_degree = networkx.in_degree_centrality(new_G)
    out_degree = networkx.out_degree_centrality(new_G)
    # eigen_degree = networkx.eigenvector_centrality_numpy(new_G)
    in_degree.pop(selected_node)
    out_degree.pop(selected_node)
    eigen_degree.pop(selected_node)
    sorted_in_degree = sorted(in_degree.items(), key=itemgetter(1), reverse=True)
    sorted_out_degree = sorted(out_degree.items(), key=itemgetter(1), reverse=True)
    # sorted_eigen_degree = sorted(eigen_degree.items(), key=itemgetter(1), reverse=True)

    in_degree_output = " "
    for n, v in sorted_in_degree[:5]:
        in_degree_output += n + " " + "{:.2f}".format(v) + '</br>'
    new_in_degree_output_div = Div(text=str(in_degree_output))
    out_degree_output = " "
    for n, v in sorted_out_degree[:5]:
        out_degree_output += n + " " + "{:.2f}".format(v) + '</br>'
    new_out_degree_output_div = Div(text=str(out_degree_output))
    dashboard.children[2].children[1] = column(analysis_text, 
        egocentric_text, selection, 
        density_text, new_density,
        in_degree_centrality_text, new_in_degree_output_div,
        out_degree_centrality_text, new_out_degree_output_div)
selection.on_change('value', callback_select)

#Remove school button
remove_school_button = Toggle(label='''Exclude schools from network''')

## reset button
## clear all the widget and return the full network
reset_button = Button(label="Reset to Full Network",  button_type='primary')
# def callback_reset():
#     target_multi_choice.value = []
#     source_multi_choice.value = []
#     target_checkbox_button_group.active = []
#     source_checkbox_button_group.active = []
#     selection.value = None
#     remove_school_button.active = False
#     layout.children[2] = plot
#     dashboard.children[2].children[1] = column(analysis_text, egocentric_text, selection, 
#                   density_text, density, 
#                   clustering_text, clustering,
#                 #   degree_centrality_text, degree_output_div,
#                   in_degree_centrality_text, in_degree_output_div,
#                   out_degree_centrality_text, out_degree_output_div,
#                   eigen_degree_centrality_text, eigen_degree_output_div)
# reset_button.on_click(callback_reset)

reset_button.js_on_click(CustomJS(args=dict(target_multi_choice=target_multi_choice,
                                            source_multi_choice=source_multi_choice,
                                            target_checkbox_button_group=target_checkbox_button_group,
                                            source_checkbox_button_group=source_checkbox_button_group,
                                            selection=selection,
                                            remove_school_button=remove_school_button
                                            ), code='''
                                            target_multi_choice.value=[];
                                            source_multi_choice.value=[];
                                            target_checkbox_button_group.active=[];
                                            source_checkbox_button_group.active=[];
                                            '''))

generate_button = Button(label="Generate",  button_type='danger')

generate_button.on_click(callback_generate)

group = row(column(source_node_txt, source_multi_choice, source_cat_txt, source_checkbox_button_group),
            column(target_node_txt, target_multi_choice, target_cat_txt, target_checkbox_button_group),
            sizing_mode='stretch_both')

layout = column(group, row(remove_school_button, generate_button, reset_button, sizing_mode="scale_width"), plot)
analysis_text = Div(text="Network Analysis", style={'font-size': '150%'})
density_text = Div(text="Density:", style={'font-weight': 'bold'})
density = Div(text="{:.2f}".format(networkx.density(G)))


clustering_text = Div(text="Clustering Coefficient:", style={'font-weight': 'bold'})
# print(networkx.average_clustering(G))
clustering = Div(text="{:.2f}".format(networkx.average_clustering(G)))

degree = networkx.degree_centrality(G)
in_degree = networkx.in_degree_centrality(G)
out_degree = networkx.out_degree_centrality(G)
eigen_degree = networkx.eigenvector_centrality(G)

sorted_degree = sorted(degree.items(), key=itemgetter(1), reverse=True)
sorted_in_degree = sorted(in_degree.items(), key=itemgetter(1), reverse=True)
sorted_out_degree = sorted(out_degree.items(), key=itemgetter(1), reverse=True)
sorted_eigen_degree = sorted(eigen_degree.items(), key=itemgetter(1), reverse=True)

degree_output = " "
for n, v in sorted_degree[:5]:
    degree_output += n + " " + "{:.2f}".format(v) + '</br>'
degree_output_div = Div(text=str(degree_output))

in_degree_output = " "
for n, v in sorted_in_degree[:5]:
    in_degree_output += n + " " + "{:.2f}".format(v) + '</br>'
in_degree_output_div = Div(text=str(in_degree_output))
out_degree_output = " "
for n, v in sorted_out_degree[:5]:
    out_degree_output += n + " " + "{:.2f}".format(v) + '</br>'
out_degree_output_div = Div(text=str(out_degree_output))
eigen_degree_output = " "
for n, v in sorted_eigen_degree[:5]:
    eigen_degree_output += n + " " + "{:.2f}".format(v) + '</br>'
eigen_degree_output_div = Div(text=str(eigen_degree_output))

degree_centrality_text = Div(text="Degree Centrality:")
in_degree_centrality_text = Div(text="Top 5 In-degree Centrality:", style={'font-weight': 'bold'})
out_degree_centrality_text = Div(text="Top 5 Out-degree Centrality:", style={'font-weight': 'bold'})
eigen_degree_centrality_text = Div(text="Top 5 Eigenvector Centrality:", style={'font-weight': 'bold'})


analysis = column(analysis_text, egocentric_text, selection, 
                  density_text, density, 
                  clustering_text, clustering,
                #   degree_centrality_text, degree_output_div,
                  in_degree_centrality_text, in_degree_output_div,
                  out_degree_centrality_text, out_degree_output_div,
                  eigen_degree_centrality_text, eigen_degree_output_div)
Title_text = Div(text= "Penn Innovation Ecosystem (PIE)", style={'font-size': '200%'})
Intro_tdxt = Div(text='''We invite you to explore the PIE as a network of "innovation nodes" that develop, commercialize, teach, and promote innovations at the University of Pennsylvania. Two innovation nodes are connected if at least one of them (source node) embeds on its website a link to the other one (target node)''')
dashboard = column(Title_text, Intro_tdxt,row(layout, analysis))
curdoc().add_root(dashboard)
# https://towardsdatascience.com/how-to-create-a-plotly-visualization-and-embed-it-on-websites-517c1a78568b

# from bokeh.plotting import figure, save, output_file
# from bokeh.resources import CDN
# from bokeh.embed import file_html

# # output_file(filename="page.html")
# # save(dashboard)
# html = file_html(dashboard, CDN, "my plot")
# print(html)