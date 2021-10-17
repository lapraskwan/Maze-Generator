import sys
import random
import matplotlib.pyplot as plt
import time
import faulthandler

faulthandler.enable()

class Maze:
	def __init__(self, height: int, width: int):
		if height < 2 or width < 2:
			print("Height and width must be equal to or larger than 2")
			sys.exit()

		self.height = height
		self.width = width

		# An list to store the nodes in the maze
		self.maze = [[] for _ in range(self.height * self.width)]

		# Initialize the maze as a fully connected maze
		for i in range(self.height * self.width):
			# Create a fully connected node
			for adj_node_idx in self.adjacent_nodes(i):
				weight = random.randint(1, 1000)
				if adj_node_idx < i:
					for edge in self.maze[adj_node_idx]:
						if edge[1] == i:
							weight = edge[0]
							break
				self.maze[i].append((weight, adj_node_idx))

		# Randomly assign a starting point and an ending point
		# Allows starting point in the left column or the top row only
		start_top = random.randint(0, self.width - 1)
		start_left = random.randint(0, self.height - 1) * self.width

		# Allows ending point in the right column or the bottom row only
		end_bottom = (self.height - 1) * self.width + random.randint(0, self.width - 1)
		end_right = random.randint(0, self.height - 1) * self.width + (self.width - 1)

		self.entrance = random.choice([start_top, start_left])
		self.destination = random.choice([end_bottom, end_right])

		# Generate a perfect maze
		self.generate_maze()

	def print_edges(self):
		""" Print the information of all edges in the maze for debug purpose """
		print("Print edges")
		counter = 0
		for i, node in enumerate(self.maze):
			for edge in node:
				print(f"From {i} to {edge[1]}. Weight: {edge[0]}")
				counter += 1
		print(f"Counter: {counter}")

	def adjacent_nodes(self, node_index):
		""" Given a node coordinate, return a list of indices of adjacent nodes in a fully connected maze (No walls) """
		x = node_index % self.width
		y = node_index // self.width

		adj_nodes = []

		# Top-left corner
		if x == 0 and y == 0:
			adj_nodes.append(self.width * y + (x + 1))
			adj_nodes.append(self.width * (y + 1) + x)

		# Top-right corner
		elif x == self.width - 1 and y == 0:
			adj_nodes.append(self.width * y + (x - 1))
			adj_nodes.append(self.width * (y + 1) + x)

		# Bottom-left corner
		elif x == 0 and y == self.height - 1:
			adj_nodes.append(self.width * (y - 1) + x)
			adj_nodes.append(self.width * y + (x + 1))

		# Bottom-right corner
		elif x == self.width - 1 and y == self.height - 1:
			adj_nodes.append(self.width * (y - 1) + x)
			adj_nodes.append(self.width * y + (x - 1))

		# Top row
		elif y == 0:
			adj_nodes.append(self.width * y + (x - 1))
			adj_nodes.append(self.width * y + (x + 1))
			adj_nodes.append(self.width * (y + 1) + x)

		# Bottom row
		elif y == self.height - 1:
			adj_nodes.append(self.width * y + (x - 1))
			adj_nodes.append(self.width * y + (x + 1))
			adj_nodes.append(self.width * (y - 1) + x)

		# Left column
		elif x == 0:
			adj_nodes.append(self.width * y + (x + 1))
			adj_nodes.append(self.width * (y - 1) + x)
			adj_nodes.append(self.width * (y + 1) + x)

		# Right column
		elif x == self.width - 1:
			adj_nodes.append(self.width * y + (x - 1))
			adj_nodes.append(self.width * (y - 1) + x)
			adj_nodes.append(self.width * (y + 1) + x)

		# All other center nodes
		else:
			adj_nodes.append(self.width * y + (x - 1))
			adj_nodes.append(self.width * y + (x + 1))
			adj_nodes.append(self.width * (y - 1) + x)
			adj_nodes.append(self.width * (y + 1) + x)

		return adj_nodes

	def generate_maze(self):
		""" Use the Prim's algorithm to generate a perfect maze """

		# Add node 0 to traversed_nodes
		traversed_nodes = [0]
		# Add all other nodes to untraversed_nodes
		untraversed_nodes = [i for i in range(1, self.height * self.width)]

		# A list to store the final set of edges in the minimum spanning tree
		mst_edges = []

		# A list to store the edges waiting for exploration
		pending_edges = []

		# Add all edges connecting to node 0 to pending_edges
		for edge in self.maze[0]:
			pending_edges.append((edge[0], 0, edge[1]))

		# Find out the minimum spanning tree
		while untraversed_nodes:
			# Sort the edges in ascending order of their weight
			pending_edges.sort()

			# Remove the edge with the minimum weight from pending_edge
			min_weight_edge = pending_edges.pop(0)
			while min_weight_edge[2] in traversed_nodes:
				# In case both points of this edge is being traversed
				min_weight_edge = pending_edges.pop(0)

			mst_edges.append(min_weight_edge)
			untraversed_nodes.remove(min_weight_edge[2])
			traversed_nodes.append(min_weight_edge[2])

			# Add all edges from the end point of the above edge to pending_edges
			for edge in self.maze[min_weight_edge[2]]:
				if edge[1] in untraversed_nodes:
					pending_edges.append((edge[0], min_weight_edge[2], edge[1]))
		
		# Remove all edges in self.maze such that only edges in mst_edges remain
		for i, node in enumerate(self.maze):
			# Cannot remove the edge directly because it will alter node.edge, which skips some iterations in the loop below
			# So a list is used to store the edges to be removed from each node
			edges_to_be_removed = []

			for edge in node:
				for mst_edge in mst_edges:
					if (mst_edge[1] == i and mst_edge[2] == edge[1]) or (mst_edge[2] == i and mst_edge[1] == edge[1]):
						break
				else:
					edges_to_be_removed.append(edge)

			for edge in edges_to_be_removed:
				node.remove(edge)

	def wall_directions(self, node):
		""" Given a node, return a list of wall directions """
		walls = ['n', 'e', 's', 'w']
		for edge in self.maze[node]:
			if edge[1] == node - 1:
				walls.remove('w')
			if edge[1] == node + 1:
				walls.remove('e')
			if edge[1] == node - self.width:
				walls.remove('n')
			if edge[1] == node + self.width:
				walls.remove('s')

		if node == self.entrance:
			if node % self.width == 0:
				walls.remove('w')
			else:
				walls.remove('n')

		if node == self.destination:
			if node % self.width == self.width - 1:
				walls.remove('e')
			else:
				walls.remove('s')
		return walls

	def plot_maze(self, solved=False):
		""" Plot the maze with matplotlib """
		# Draw the shortest path if solved=True
		if solved:
			path = self.solve_maze()
			for i, node in enumerate(path):
				if i != len(path) - 1:
					# xy coordinates of the center of the current node
					x_0 = node % self.width + 0.5
					y_0 = node // self.width + 0.5

					# xy coordinates of the center of the current node
					x_1 = path[i+1] % self.width + 0.5
					y_1 = path[i+1] // self.width + 0.5

					plt.plot([x_0, x_1], [y_0, y_1], 'r-')

		# Draw the maze
		for node in range(len(self.maze)):
			x = node % self.width
			y = node // self.width

			for wall in self.wall_directions(node):
				if wall == 'n':
					plt.plot([x, x + 1], [y, y], 'b-')
				if wall == 'e':
					plt.plot([x + 1, x + 1], [y, y + 1], 'b-')
				if wall == 's':
					plt.plot([x, x + 1], [y + 1, y + 1], 'b-')
				if wall == 'w':
					plt.plot([x, x], [y, y + 1], 'b-')

		plt.gca().invert_yaxis()
		plt.show()

	def solve_maze(self):
		""" Solve the maze using BFS, return the path """
		paths = [[self.entrance]]
		explored_nodes = []

		while paths:
			path = paths.pop(0)
			current_node = path[-1]

			# To keep track of the percentage of nodes explored
			if current_node not in explored_nodes:
				explored_nodes.append(current_node)
				if len(explored_nodes) % (self.height * self.width // 10) == 0:
					print(f"{len(explored_nodes) / (self.height * self.width) * 100}% explored.")

			if current_node == self.destination:
				return path
			for edge in self.maze[current_node]:
				if edge[1] not in path:
					new_path = path[:]
					new_path.append(edge[1])
					paths.append(new_path)

if __name__ == "__main__":
	height = 50
	width = 50

	start_time = time.time()
	maze = Maze(height, width)
	end_time = time.time()

	maze.plot_maze(solved=True)

	print(f"Time used for generating the maze: {end_time - start_time} seconds")
