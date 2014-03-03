package br.uff.ic.sel.noworkflow.view;

import br.uff.ic.sel.noworkflow.model.Flow;
import br.uff.ic.sel.noworkflow.model.FunctionCall;
import edu.uci.ics.jung.algorithms.layout.ISOMLayout;
import edu.uci.ics.jung.algorithms.layout.Layout;
import edu.uci.ics.jung.graph.DirectedGraph;
import edu.uci.ics.jung.graph.DirectedSparseGraph;
import edu.uci.ics.jung.visualization.VisualizationViewer;
import edu.uci.ics.jung.visualization.control.DefaultModalGraphMouse;
import java.awt.BasicStroke;
import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Paint;
import java.awt.Stroke;
import java.util.Collection;
import org.apache.commons.collections15.Transformer;

public class GraphFrame extends javax.swing.JFrame {

    private long minDuration = Long.MAX_VALUE;
    private long maxDuration = 0;

    /**
     * Creates new form GraphFrame
     */
    public GraphFrame(Collection<FunctionCall> functionCalls, Collection<Flow> flows) {
        setDefaultCloseOperation(javax.swing.WindowConstants.EXIT_ON_CLOSE);
        setTitle("noWorkflow Graph Visualizer");
        setSize(800, 600);
        setLocationRelativeTo(null);

        DirectedGraph<FunctionCall, Flow> graph = getGraph(functionCalls, flows);

        for (FunctionCall functionCall : functionCalls) {
            long meanDuration = functionCall.getMeanDuration();
            this.minDuration = Math.min(this.minDuration, meanDuration);
            this.maxDuration = Math.max(this.maxDuration, meanDuration);
        }

        VisualizationViewer<FunctionCall, Flow> viewer = getViewer(graph);

        getContentPane().setLayout(new BorderLayout());
        getContentPane().add(viewer, BorderLayout.CENTER);
    }

    private DirectedGraph<FunctionCall, Flow> getGraph(Collection<FunctionCall> functionCalls, Collection<Flow> flows) {
        DirectedGraph<FunctionCall, Flow> graph = new DirectedSparseGraph<>();
        for (FunctionCall functionCall : functionCalls) {
            graph.addVertex(functionCall);
        }
        for (Flow flow : flows) {
            graph.addEdge(flow, flow.getSource(), flow.getTarget());
        }
        return graph;
    }

    private VisualizationViewer<FunctionCall, Flow> getViewer(DirectedGraph<FunctionCall, Flow> graph) {
        // Choosing layout
        Layout<FunctionCall, Flow> layout = new ISOMLayout<>(graph);
        VisualizationViewer<FunctionCall, Flow> viewer = new VisualizationViewer<>(layout);

        // Adding interation via mouse
        DefaultModalGraphMouse mouse = new DefaultModalGraphMouse();
        viewer.setGraphMouse(mouse);
        viewer.addKeyListener(mouse.getModeKeyListener());

        // Labelling vertices
        Transformer vertexLabeller = new Transformer<FunctionCall, String>() {
            @Override
            public String transform(FunctionCall functionCall) {
                return functionCall.getName();
            }
        };
        viewer.getRenderContext().setVertexLabelTransformer(vertexLabeller);

        // Labelling edges
        Transformer edgeLabeller = new Transformer<Flow, String>() {
            @Override
            public String transform(Flow flow) {
                return Integer.toString(flow.getTransitionCount());
            }
        };
        viewer.getRenderContext().setEdgeLabelTransformer(edgeLabeller);

        // Painting vertices according to the execution duration (traffic light scale)
        viewer.getRenderContext().setVertexFillPaintTransformer(new Transformer<FunctionCall, Paint>() {
            @Override
            public Paint transform(FunctionCall functionCall) {
                int tone = Math.round(255 * (functionCall.getMeanDuration() - minDuration) / (float) (maxDuration - minDuration));
                return new Color(tone, 255 - tone, 0);
            }
        });

        // Set the flow stroke (dashed or plain line, tickness, etc)
        viewer.getRenderContext().setEdgeStrokeTransformer(new Transformer<Flow, Stroke>() {
            @Override
            public Stroke transform(Flow flow) {
                float width;
                float[] dash;
                if (flow.isCall()) {
                    width = 2;
                    dash = null;
                } else if (flow.isSequence()) {
                    width = 1;
                    dash = null;
                } else { // flow.isReturn()
                    width = 2;
                    dash = new float[1];
                    dash[0] = 5;
                }
                return new BasicStroke(width, BasicStroke.CAP_ROUND, BasicStroke.JOIN_MITER, 10, dash, 0);
            }
        });

        // Painting edges
        Transformer edgePainter = new Transformer<Flow, Paint>() {
            @Override
            public Paint transform(Flow indication) {
                int tone = Math.round(0); // * ( 1 - indication.getSource().getNominationsCount() / (float) Function.getMaxNominationsCount() ));
                return new Color(tone, tone, tone);
            }
        };
        viewer.getRenderContext().setEdgeDrawPaintTransformer(edgePainter);
        viewer.getRenderContext().setArrowDrawPaintTransformer(edgePainter);
        viewer.getRenderContext().setArrowFillPaintTransformer(edgePainter);

        viewer.setBackground(Color.white);

        return viewer;
    }
}
