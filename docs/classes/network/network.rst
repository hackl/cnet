*******
Network
*******

Overview
========
.. currentmodule:: cnet
.. autoclass:: Network

Methods
=======

Properties
----------

.. autosummary::
   :toctree: generated/

   Network.__init__
   Network.__repr__
   Network._desc
   Network.__getitem__
   Network.__setitem__
   Network.shape
   Network.directed
   Network.update

Mapping functions
-----------------

.. autosummary::
   :toctree: generated/

   Network.edge_to_nodes_map
   Network.node_to_edges_map
   Network.nodes_to_edges_map

Reporting nodes and edges
-------------------------

.. autosummary::
   :toctree: generated/

   Network.name
   Network.has_node
   Network.has_edge
   Network.summary

Counting nodes and edges
------------------------

.. autosummary::
   :toctree: generated/

   Network.number_of_nodes
   Network.number_of_edges
   Network.degree

Adding and removing nodes and edges
-----------------------------------

.. autosummary::
   :toctree: generated/

   Network.add_node
   Network.add_nodes_from
   Network.remove_node
   Network.remove_nodes_from
   Network.add_edge
   Network.add_edges_from
   Network.remove_edge
   Network.remove_edges_from

Matrices
--------

.. autosummary::
   :toctree: generated/

   Network.weights
   Network.adjacency_matrix
   Network.transition_matrix
   Network.laplacian_matrix

Data handling
-------------
.. autosummary::
   :toctree: generated/

   Network.save
   Network.load
   Network.copy
