if (remove_school) {
    console.log(node_data_filtered['Name'].length)
    if (node_data_filtered['Name'].length === 0) {
        console.log('exclude school from all nodes', init_node_source)
        node_data_filtered = init_node_source
    }
    console.log("remove school", node_data_filtered)
    for (let i = 0; i < node_data_filtered['index'].length; i++) {
        if (node_data_filtered['category'][i].includes('Teaching')) {
            console.log(i)
            node_data_filtered['Name'].splice(i);
            node_data_filtered['URL'].splice(i);
            node_data_filtered['adjusted_node_size'].splice(i);
            node_data_filtered['category'].splice(i);
            node_data_filtered['degree'].splice(i);
            node_data_filtered['index'].splice(i);
        }
    }
    // source nodes
    //for (let k = 0; k < source_nodes.length; k++) {
    //    if (category[i].includes(source_nodes[k])) {
    //        source_nodes.splice(index[i]);
    //    }
    //}
    source_nodes = source_nodes.filter( (x) => !teaching_nodes.includes(x));
    target_nodes = target_nodes.filter( (x) => !teaching_nodes.includes(x));
    console.log(source_nodes)
    // target nodes
    //for (let a = 0; a < target_labels.length; a++) {
    //    if (category[i].includes(target_labels[a])) {
    //        target_nodes.push(index[i]);
    //    }
    //}
    console.log(label_source_filter);
    for (let b = 0; b < label_source_filter.length; b++) {
        if (label_source_filter['name'][b].includes(teaching_nodes)) {
            label_source_filter['x'].splice(b);
            label_source_filter['y'].splice(b);
            label_source_filter['name'].splice(b);
        }
    }

}