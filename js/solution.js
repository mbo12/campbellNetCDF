var captionHeight = 100;
var margin = {top: 0, right: 70, bottom: 0, left:130},
    width = 700 - margin.left - margin.right,
    height = 475 - margin.top - margin.bottom-captionHeight;

var tree = d3.layout.tree()
    .size([height, width]);

var diagonal = d3.svg.diagonal()
    .projection(function(d) { return [width -d.y, d.x];});

var svg = d3.select("#solution").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height+margin.top + margin.bottom+captionHeight)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

   var links = [{"source":"NetCDF file", "target":"metadata XML"},{"source":"metadata XML","target":"datalogger code"},{"source":"metadata XML","target":"sensor ID"},{"source":"metadata XML","target":"site info"},{"target":"observations","source":"metadata XML"}];
   var nodesByName = {};
   links.forEach(function(link) {
      var parent = link.source = nodeByName(link.source),
          child = link.target = nodeByName(link.target);
      if (parent.children) parent.children.push(child);
      else parent.children = [child];
   });


   var nodes = tree.nodes(links[0].source);
console.log(nodes);
   svg.selectAll(".link")
     .data(links)
     .enter().append("path")
     .attr("class","link")
     .attr("d",diagonal);

nodes =   svg.selectAll(".node")
      .data(nodes)
      .enter().append("g");

nodes.append("rect")
      .attr("y",function(d) { return d.x-30;})
      .attr("x",function(d) { return width-d.y-60;})
      .attr("rx",5)
      .attr("ry",5)
      .attr("height",60)
      .attr("width",120)
      .attr("fill","white")
      .attr("stroke","green")
      .attr("stroke-width","3px");
nodes
      .append("text") 
      .attr("fill","black")
      .attr("dy", ".35em")
      .attr("x",function(d) { return width - d.y;})
      .attr("y",function(d) { return d.x ;})
      .attr("text-anchor","middle")
      .text(function(d) { return d.name; });


svg.append("foreignObject")
    .attr("x",0)
    .attr("y",height+margin.top)
    .attr("width",width)
    .attr("height",100)
    .append("xhtml:body")
    .style("font", "14px sans-serif")
    .style("padding-top","0")
    .html("<p><b>How it works:</b> We programmatically pull in relevant metadata from CRBasic datalogger code. We also make it easy to incorporate user-input, such as sensor id, site info, observation units, and more. The metadata is stored as an XML, where it can be a stand-alone documentation source. The metadata is then pulled into the NetCDF format, where it serves as attributes for the variables.");

  function nodeByName(name) {
     return nodesByName[name] || (nodesByName[name] = {name: name});

  }
