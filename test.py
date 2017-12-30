from PySide.QtCore import *
from PySide.QtGui import *
from functools import partial

selected_port = None

class Connection(QGraphicsLineItem):

    def __init__(self, src, dest):
        QGraphicsLineItem.__init__(self)
        self.src = src
        self.dest = dest
        self.updateEndpoints()
        self.src.node.scene.addItem(self)

    def updateEndpoints(self):
        p1 = self.src.sceneBoundingRect().center()
        p2 = self.dest.sceneBoundingRect().center()
        self.setLine(p1.x(), p1.y(), p2.x(), p2.y())

class Port(QGraphicsRectItem):

    def __init__(self, node, index, name, is_output):
        QGraphicsRectItem.__init__(self)
        yoffset = node.y() + 30 + index * 20
        self.node = node
        self.connections = []
        self.setParentItem(node)
        self.setRect(node.x() + 90 if is_output else 0, yoffset, 10, 10)
        self.setBrush(Qt.green if is_output else Qt.yellow)
        self.setFlag(self.ItemIsSelectable, True)
        self.setFlag(self.ItemSendsScenePositionChanges, True)
        label = QGraphicsSimpleTextItem(name)
        width = label.boundingRect().width()
        label.setParentItem(node)
        label.setPos(node.x() + 80 - width if is_output else 20, yoffset)

    def itemChange(self, change, value):
        global selected_port
        if change == self.ItemSelectedChange and value:
            if selected_port:
                self.connect_to(selected_port)
                selected_port = None
                return False
            else:
                selected_port = self
                return True
        elif change == self.ItemScenePositionHasChanged:
            for c in self.connections:
                c.updateEndpoints()
        return QGraphicsRectItem.itemChange(self, change, value)

    def connect_to(self, other):
        conn = Connection(self, other)
        self.connections.append(conn)
        other.connections.append(conn)

class Node(QGraphicsRectItem):

    def __init__(self, scene, name, inputs, outputs):
        QGraphicsRectItem.__init__(self)
        self.scene = scene
        self.setRect(0, 0, 100, 30 + 20 * max(len(inputs), len(outputs)))
        self.setBrush(Qt.darkCyan)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        label = QGraphicsSimpleTextItem(name)
        label.setParentItem(self)
        label.setPos(self.x() + 10, self.y() + 10)
        for i, input_name in enumerate(inputs):
            Port(self, i, input_name, False)
        for i, output_name in enumerate(outputs):
            Port(self, i, output_name, True)

node_types = ["Foo", "Bar"]

app = QApplication(["Flowgraph UI"])
window = QWidget()
layout = QVBoxLayout()
menubar = QMenuBar()
add_menu = menubar.addMenu("Add block")
scene = QGraphicsScene()

def add_node(name):
    scene.addItem(Node(scene, name, ["in1", "in2"], ["out1", "out2", "out3"]))

for name in node_types:
    add_menu.addAction(name, partial(add_node, name))

graphics = QGraphicsView(scene)
layout.addWidget(menubar)
layout.addWidget(graphics)
window.setLayout(layout)
window.show()
app.exec_()
