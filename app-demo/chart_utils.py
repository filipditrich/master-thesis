from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class SankeyNode:
	id: str
	label: str
	x: float
	y: float
	color: str


@dataclass
class SankeyFlow:
	source: str
	target: str
	value: float
	color: str


colors = {
	'indigo': 'rgba(101, 116, 205, 1.0)',  # Soft indigo for online
	'cool_gray': 'rgba(149, 165, 166, 1.0)',  # Professional gray
	'slate_blue': 'rgba(162, 181, 205, 1.0)',  # Slate blue for payments
	'light_steel': 'rgba(176, 190, 197, 1.0)',  # Light steel blue
	'warm_gray': 'rgba(188, 184, 177, 1.0)',  # Warm gray
	'sage': 'rgba(134, 179, 167, 1.0)',  # Sage green
	'dusty_blue': 'rgba(130, 177, 197, 1.0)',  # Dusty blue
	'lavender': 'rgba(156, 147, 190, 1.0)',  # Soft lavender
	'rose': 'rgba(199, 144, 144, 1.0)',  # Dusty rose
	'mint': 'rgba(134, 182, 151, 1.0)',  # Mint green
	'peach': 'rgba(226, 139, 120, 1.0)',  # Soft peach
}

chart_colors = {
	'chart1': '#2D7DD2',
	'chart2': '#6C969D',
	'chart3': '#97CC04',
	'chart4': '#EEB902',
	'chart5': '#474647',
	'chart6': '#F45D01',
	'chart7': '#9B6B6C',
	'chart8': '#556F44',
}


def get_chart_color(name: str) -> str:
	return chart_colors[name] if name in chart_colors else chart_colors['chart1']


def get_color(name: str, alpha: Optional[float] = None) -> str:
	base_color = colors[name] if name in colors else colors['indigo']
	if alpha is not None:
		return change_alpha(base_color, alpha)


def change_alpha(color: str, alpha: float) -> str:
	return color[:-4] + str(alpha) + ")"


class SankeyDiagram:
	def __init__(self):
		self.nodes: Dict[str, SankeyNode] = { }
		self.flows: List[SankeyFlow] = []

	def add_node(self, id: str, label: str, x: float, y: float, color: str) -> None:
		"""Add a node to the diagram"""
		self.nodes[id] = SankeyNode(id=id, label=label, x=x, y=y, color=get_color(color, 0.85))

	def add_flow(self, source: str, target: str, value: float, color: Optional[str]) -> None:
		"""Add a flow between nodes"""
		source_node = self.nodes.get(source)
		self.flows.append(
			SankeyFlow(
				source=source,
				target=target,
				value=value,
				color=get_color(color, 0.35) if color else change_alpha(source_node.color, 0.35) if source_node else get_color('slate', 0.35)
			)
		)

	def to_plotly(self) -> dict:
		"""Convert to plotly Sankey format"""
		# Create node index mapping
		node_indices = { node_id: i for i, node_id in enumerate(self.nodes.keys()) }

		# Create node lists
		node_x = [node.x for node in self.nodes.values()]
		node_y = [node.y for node in self.nodes.values()]
		node_colors = [node.color for node in self.nodes.values()]
		node_labels = [node.label for node in self.nodes.values()]

		# Create flow lists
		sources = [node_indices[flow.source] for flow in self.flows]
		targets = [node_indices[flow.target] for flow in self.flows]
		values = [flow.value for flow in self.flows]
		flow_colors = [flow.color for flow in self.flows]

		return {
			'node': {
				'pad': 20,
				'thickness': 20,
				'line': { 'color': "black", 'width': 0.5 },
				'label': node_labels,
				# 'x': node_x,
				# 'y': node_y,
				'color': node_colors,
			},
			'link': {
				'source': sources,
				'target': targets,
				'value': values,
				'color': flow_colors,
			}
		}
