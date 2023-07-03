# This is the python script to generate network visualization of PIE
# Required file: network.cvs, site_domainV2.xlsx
# output index.html file
# https://programminghistorian.org/en/lessons/exploring-and-analyzing-network-data-with-python
# To run the file: 
# enter the following command in Terminal: bokeh serve --show network_viz.py
# for development: BOKEH_MINIFIED=no bokeh serve --dev --show network_viz.py
#Import Libraries
# !pip install pyvis
# !pip install Network
# !pip install TapTool
# !pip install bokeh
# from bokeh.io import output_notebook, show, save

import pandas as pd
import networkx
from operator import itemgetter
from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine, Toggle
from bokeh.plotting import figure, curdoc, from_networkx
from bokeh.models import EdgesAndLinkedNodes, NodesAndLinkedEdges, LabelSet
from bokeh.palettes import Blues8, Spectral8

"""#Data Loading"""
df = pd.read_csv("./bokeh-app/data/network.csv")
print("reading data")
df.rename(columns={'domains_clean':'source', 'embedded_domains':'target', 'embedded_domains.1':'count'}, inplace=True)
start = 1
end = 10
width = end - start
df['weight'] =(df['count']-df['count'].min())/(df['count'].max()-df['count'].min())*width+start
df = df[df['target']!='None']
df['source_truncated'] = df['source'].apply(lambda x: x.replace('.upenn.edu',''))
df['target_truncated'] = df['target'].apply(lambda x: x.replace('.upenn.edu',''))

df_cat = pd.read_excel("./bokeh-app/data/site_domainV2.xlsx", sheet_name='domain')
df_cat['Category'] = df_cat[['R&D','Teaching','Organizer', 'Knowledge', 'Media']].apply(lambda x: ','.join(x[x.isnull()==False].index), axis=1)
df_cat['domain_truncated'] = df_cat['domain'].apply(lambda x: x.split('/')[2].replace('www.','').replace('.upenn.edu',''))

url_class = dict(zip(df_cat['Node_Name'],df_cat['domain']))
category_class = dict(zip(df_cat['Node_Name'],df_cat['Category']))
index_class = dict(zip(df_cat['domain_truncated'],df_cat['Node_Name']))
name_class = dict(zip(df_cat['Node_Name'],df_cat['Popup_Name']))

school_nodes = df_cat[df_cat['School'] == 1]['Node_Name'].to_list()
df['source_name'] = df['source_truncated'].map(index_class)
df['target_name'] = df['target_truncated'].map(index_class)
df['source_category'] = df['source_name'].map(category_class)
df['target_category'] = df['target_name'].map(category_class)
target_domains_sorted = sorted(df['target_truncated'].map(index_class).unique())
source_domains_sorted = sorted(df['source_truncated'].map(index_class).unique())
domains_sorted = sorted(df[df['source_category'].str.contains('Teaching')==False]['source_name'].unique())

"""#Network(interactive)"""
from bokeh.core.enums import SizingMode
from bokeh.io import show
from bokeh.models import CustomJS, MultiChoice
from bokeh.io.output import output_file
from bokeh.models import Button, CustomJS, Div, CheckboxButtonGroup, TapTool, OpenURL, Select
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource
from bokeh.io import show

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

labels = ["R&D", "Teaching", "Organizer", "Knowledge", "Media"]

## Source
source_node_txt = Div(text="Select Source Node(s):")
source_checkbox_button_group = CheckboxButtonGroup(labels=labels)
source_cat_txt = Div(text="Select Source Types(s):")
source_multi_choice = MultiChoice(options=source_domains_sorted)

## Target
target_node_txt = Div(text="Select Target Node(s):")
target_checkbox_button_group = CheckboxButtonGroup(labels=labels)
target_cat_txt = Div(text="Select Target Type(s):")
target_multi_choice = MultiChoice(options=target_domains_sorted, height=500)

#Remove school button
remove_school_button = Toggle(label='''Exclude schools from network''')

def make_dataset():
    G = networkx.from_pandas_edgelist(df, 'source_name', 'target_name', edge_attr=['weight'], create_using=networkx.DiGraph())
    node_labels = list(G.nodes())

    #Calculate degree for each node and add as node attribute
    degrees = dict(networkx.degree(G))
    networkx.set_node_attributes(G, name='degree', values=degrees)

    # #Slightly adjust degree so that the nodes with very small degrees are still visible
    number_to_adjust_by = 5
    adjusted_node_size = dict([(node, degree+number_to_adjust_by) for node, degree in networkx.degree(G)])
    networkx.set_node_attributes(G, name='adjusted_node_size', values=adjusted_node_size)
    networkx.set_node_attributes(G, url_class, "URL")
    networkx.set_node_attributes(G, category_class, "category")
    networkx.set_node_attributes(G, name_class, "Name")
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

    return network_graph, node_labels

def make_plot(src):
    #Create a plot — set dimensions, toolbar, and title
    plot = figure(tooltips = HOVER_TOOLTIPS,
                tools="pan,tap,wheel_zoom,save,reset",
                x_range=Range1d(-15.1, 15.1), y_range=Range1d(-15.1, 15.1), toolbar_location="left",
                width=800, height=600)
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = None
    plot.axis.visible=False
    plot.toolbar.logo = None

    # Configure tap tool
    taptool = plot.select(type=TapTool)
    taptool.callback = OpenURL(url="@URL")
    plot.renderers.append(src)

    return plot

# Update the plot based on selections
# def update(attr, old, new):
    # carriers_to_plot = [carrier_selection.labels[i] for i in carrier_selection.active]
    # network_graph, node_labels = make_dataset()
    # new_src = make_dataset(carriers_to_plot,
    #                        range_start = range_select.value[0],
    #                        range_end = range_select.value[1],
    #                        bin_width = binwidth_select.value)

    # attr.data.update(network_graph)

network_graph, node_labels = make_dataset()
plot = make_plot(network_graph)

#Add Labels
x, y = zip(*network_graph.layout_provider.graph_layout.values())
label_source = ColumnDataSource({'x': x, 'y': y, 'name': node_labels})
node_labelset = LabelSet(x='x', y='y', text='name', source=label_source, background_fill_color='white', text_font_size='10px', background_fill_alpha=.8)
plot.renderers.append(node_labelset)

init_node_source = network_graph.node_renderer.data_source.data.copy()
init_edge_source = network_graph.edge_renderer.data_source.data.copy()
init_label_source = label_source.data.copy()
callback = CustomJS(args=dict(init_node_source=init_node_source,
                              filtered_node_source=network_graph.node_renderer.data_source,
                              init_edge_source=init_edge_source,
                              filtered_edge_source=network_graph.edge_renderer.data_source,
                              init_label_source=init_label_source,
                              filtered_label_source=label_source,
                              school_nodes = school_nodes,
                              source_checkbox_button_group=source_checkbox_button_group,
                              source_multi_choice=source_multi_choice,
                              target_checkbox_button_group=target_checkbox_button_group,
                              target_multi_choice=target_multi_choice,
                              remove_school_button=remove_school_button), code="""
    var remove_school = remove_school_button.active;
    let node_data = init_node_source;

    // Name, URL, adjusted_node_size, category, degree, index
    // Create filtered data framework
    var node = {};
    var data_name = [];
    var data_url = [];
    var data_adjusted_node_size = [];
    var data_category = [];
    var data_degree = [];
    var data_index = [];

    // Extracting data from dictionary
    const name = node_data['Name'];
    const url = node_data['URL'];
    const adjusted_node_size = node_data['adjusted_node_size'];
    const category = node_data['category'];
    const degree = node_data['degree'];
    const index = node_data['index'];
    
    // extract values from multiple choice
    let s = new Set(source_multi_choice.value);
    var source_nodes = [...new Set(source_multi_choice.value)];
    var target_nodes = [...new Set(target_multi_choice.value)];

    // extract values from selected category
    var source_labels = Array.from(source_checkbox_button_group.active, a => isNaN(source_checkbox_button_group.labels[a]) ? source_checkbox_button_group.labels[a] : Number(source_checkbox_button_group.labels[a]));
    var target_labels = Array.from(target_checkbox_button_group.active, a => isNaN(target_checkbox_button_group.labels[a]) ? target_checkbox_button_group.labels[a] : Number(target_checkbox_button_group.labels[a]));
    var selected_category = [];
    var selected_node = [];
    selected_category = Array.from(new Set(source_labels.concat(target_labels)));
    selected_node = Array.from(new Set(source_nodes.concat(target_nodes)));

    for (let i = 0; i < category.length; i++) {
        for (let j = 0; j < selected_category.length; j++) {
            if (remove_school != true && category[i].includes(selected_category[j]) && !data_index.includes(index[i])) {
                data_name.push(name[i]);
                data_url.push(url[i]);
                data_adjusted_node_size.push(adjusted_node_size[i]);
                data_category.push(category[i]);
                data_degree.push(degree[i]);
                data_index.push(index[i]);
            } else if (remove_school && !school_nodes.includes(index[i]) && category[i].includes(selected_category[j]) && !data_index.includes(index[i])) {
                data_name.push(name[i]);
                data_url.push(url[i]);
                data_adjusted_node_size.push(adjusted_node_size[i]);
                data_category.push(category[i]);
                data_degree.push(degree[i]);
                data_index.push(index[i]);
            }
        }
    }

    for (let i = 0; i < index.length; i++) {
        // selected nodes  
        for (let j = 0; j < selected_node.length; j++) {
            if (index[i].includes(selected_node[j]) && !data_index.includes(index[i])) {
                data_name.push(name[i]);
                data_url.push(url[i]);
                data_adjusted_node_size.push(adjusted_node_size[i]);
                data_category.push(category[i]);
                data_degree.push(degree[i]);
                data_index.push(index[i]);
            }
        }
        // source nodes
        for (let k = 0; k < source_labels.length; k++) {
            if (category[i].includes(source_labels[k])) {
                source_nodes.push(index[i]);
            }
        }
        // target nodes
        for (let a = 0; a < target_labels.length; a++) {
            if (category[i].includes(target_labels[a])) {
                target_nodes.push(index[i]);
            }
        }

    }

    source_nodes = source_nodes.filter( (x) => !school_nodes.includes(x));
    target_nodes = target_nodes.filter( (x) => !school_nodes.includes(x));

    node['Name'] = data_name;
    node['URL'] = data_url;
    node['adjusted_node_size'] = data_adjusted_node_size;
    node['category'] = data_category;
    node['degree'] = data_degree;
    node['index'] = data_index;

    node_data = node;
    filtered_node_source.data = node_data;
    filtered_node_source.change.emit();

    // filter label 
    let label_data = init_label_source;
    const x = label_data['x'];
    const y = label_data['y'];
    const label = label_data['name'];

    //var label_source_filter = {'x':[],'y':[],'name':[]};
    var ll = {};
    var label_x = [];
    var label_y = [];
    var label_name = [];
    // label

    for (let b = 0; b < label_data.name.length; b++) {
        if (data_index.includes(label_data.name[b])) {
            label_x.push(x[b]);
            label_y.push(y[b]);
            label_name.push(label_data.name[b]);
        }
    }
    ll['x'] = label_x;
    ll['y'] = label_y;
    ll['name'] = label_name;
    label_data=ll;
    filtered_label_source.data = label_data;
    //filtered_label_source.emit();

    // filter edge
    // var edge = {'end':[],'line_width':[],'start':[],'weight':[]};
    var edge = {};
    var edge_end = [];
    var edge_line_width = [];
    var edge_start = [];
    var edge_weight = [];
    let edge_data = init_edge_source;

    const line_width = edge_data['line_width'];
    const weight = edge_data['weight'];
    const start = edge_data['start'];
    const end = edge_data['end'];
    for (let i = 0; i < start.length; i++) {
        var source = start[i];
        var target = end[i];
        for (let j = 0; j < source_nodes.length; j++) {
            if (source === source_nodes[j]) {
                for (let z = 0; z < target_nodes.length; z++) {
                    if (target === target_nodes[z]) {
                        edge_end.push(end[i]);
                        edge_line_width.push(line_width[i]);
                        edge_start.push(start[i]);
                        edge_weight.push(weight[i]);
                    }
                }
            }
        }
    } 

    edge['end'] = edge_end;
    edge['line_width'] = edge_line_width;
    edge['start'] = edge_start;
    edge['weight'] = edge_weight;
    edge_data = edge;
    filtered_edge_source.data = edge_data;
    filtered_edge_source.change.emit();
    """)

# reset button
# clear all the widget and return the full network
reset_button = Button(label="Reset to Full Network",  button_type='primary')

# JS code for callback reset
callback_reset = CustomJS(args=dict(node_source=network_graph.node_renderer.data_source, init_node_source=init_node_source,
                              edge_source=network_graph.edge_renderer.data_source, init_edge_source = init_edge_source,
                              label_source=label_source, init_label_source=init_label_source,
                              source_checkbox_button_group=source_checkbox_button_group,
                              source_multi_choice=source_multi_choice,
                              target_checkbox_button_group=target_checkbox_button_group,
                              target_multi_choice=target_multi_choice,
                              remove_school_button=remove_school_button), code="""
    target_multi_choice.value = [];
    source_multi_choice.value = [];
    target_checkbox_button_group.active = [];
    source_checkbox_button_group.active = [];
    node_source.data=init_node_source;
    remove_school_button.active=false;
    edge_source.data=init_edge_source;
    label_source.data=init_label_source;
    node_source.change.emit();
    edge_source.change.emit();
    label_source.change.emit();
    """)
reset_button.js_on_click(callback_reset)

generate_button = Button(label="Generate",  button_type='danger')
generate_button.js_on_click(callback)

def mk_div(**kwargs):
    return Div(text='<div style="background-color: transparent; width: 100px; height: 50px;"></div>', **kwargs)

select_group = column(source_node_txt, source_multi_choice, mk_div(), source_cat_txt, source_checkbox_button_group,
                    target_node_txt, target_multi_choice, mk_div(), target_cat_txt, target_checkbox_button_group, mk_div(),
                    remove_school_button, row(generate_button, reset_button, sizing_mode="stretch_width"),sizing_mode="stretch_height",width=400)

# select_group = column(source_node_txt, source_multi_choice, mk_div(), source_cat_txt, source_checkbox_button_group,
#                     target_node_txt, target_multi_choice, mk_div(), target_cat_txt, target_checkbox_button_group, mk_div(),
#                     remove_school_button, row(generate_button, sizing_mode="stretch_width"),sizing_mode="stretch_height",width=400)


layout = row(plot, select_group)

curdoc().add_root(layout)
# https://towardsdatascience.com/how-to-create-a-plotly-visualization-and-embed-it-on-websites-517c1a78568b

from bokeh.plotting import figure, save, output_file
from bokeh.resources import CDN
from bokeh.embed import file_html

html = file_html(layout, CDN, "my plot")

# Creating an HTML file
Func = open("index.html","w")
   
# Adding input data to the HTML file
Func.write(html)
              
Func.close()