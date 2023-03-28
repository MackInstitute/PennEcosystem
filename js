from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import CustomJS, ColumnDataSource, Select
from bokeh.plotting import figure
from bokeh.models.graphs import from_networkx
from networkx import karate_club_graph

# create a graph
G = karate_club_graph()

# create a Bokeh figure and graph from the graph
plot = figure(title='Karate Club Graph', x_range=(-2.1, 2.1), y_range=(-2.1, 2.1))
graph = from_networkx(G, from_networkx.spring_layout, scale=2, center=(0, 0))
plot.renderers.append(graph)

# create a ColumnDataSource object with the node attributes
node_data = dict(index=list(G.nodes), group=[G.nodes[i]['club'] for i in G.nodes])
node_source = ColumnDataSource(node_data)

# create a dropdown menu to select the node group
group_select = Select(title='Node Group:', options=list(set(node_data['group'])))

# create a callback function that updates the node colors and edhhges based on the selected node group
callback = CustomJS(args=dict(node_source=node_source, graph_renderer=graph.node_renderer), code="""
    const data = node_source.data;
    const group = data['group'];
    const edges = graph_renderer.data_source.data['edge_index'];
    const colors = {'Mr. Hi': 'red', 'Officer': 'blue'};
    for (let i = 0; i < group.length; i++) {
        if (group[i] === cb_obj.value) {
            node_source.data.fill_color[i] = colors[group[i]];
        } else {
            node_source.data.fill_color[i] = 'gray';
        }
    }
    for (let i = 0; i < edges.length; i += 2) {
        const source_index = edges[i];
        const target_index = edges[i + 1];
        if (group[source_index] === cb_obj.value && group[target_index] === cb_obj.value) {
            graph_renderer.data_source.data.line_color[i / 2] = colors[group[source_index]];
        } else {
            graph_renderer.data_source.data.line_color[i / 2] = 'gray';
        }
    }
    node_source.change.emit();
    graph_renderer.data_source.change.emit();
""")

# attach the callback to the dropdown menu
group_select.js_on_change('value', callback)

# set the node colors and edge colors based on the 'group' attribute
graph.node_renderer.data_source.data['fill_color'] = [node_data['group'][i] for i in graph.node_renderer.data]

