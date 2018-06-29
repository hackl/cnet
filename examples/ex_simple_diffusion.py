#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : ex_simple_diffusion.py -- Example of diffusion
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-06-27
# Time-stamp: <Fre 2018-06-29 14:04 juergen>
#
# Copyright (c) 2018 Juergen Hackl <hackl@ibi.baug.ethz.ch>
# =============================================================================
import os
import sys
from network2tikz import plot
from ex_networks import scholtes, scholtes_second_order, sioux_falls


wk_dir = os.path.dirname(os.path.realpath('__file__'))
sys.path.insert(0, os.path.abspath(os.path.join(wk_dir, '..')))

import cnet
from cnet.algorithms.diffusion import RandomWalkDiffusion


def main():
    # initialize the network
    # network = scholtes()
    network = scholtes_second_order()
    # network = sioux_falls()

    # print the summary of the network
    network.summary()

    # plot the network
    # visual style
    layout = network.nodes['coordinate']
    visual_style = {}
    visual_style['layout'] = layout
    visual_style['node_label_as_id'] = True
    visual_style['node_color'] = 'red'
    visual_style['node_opacity'] = 1
    visual_style['edge_label'] = [e for e in network.edges]
    visual_style['edge_curved'] = 0.05
    visual_style['canvas'] = (10, 10)

    # define diffusion process
    rwd = RandomWalkDiffusion(network)

    print(rwd.speed())
    # run over several time steps
    for i in range(55):
        print('Step: {num:02d}'.format(num=i))

        # change the opacity of the nodes according to the diffusion process
        visual_style['node_opacity'] = rwd.step(i, node=network.nodes[0].id)

        # add the time step to the file name
        filename = './temp/pdfs/{num:02d}_network.pdf'.format(num=i)

        # Save each time step as a pdf network
        plot(network, filename, **visual_style)

    # convert pdf's into a single file
    os.system('pdftk ./temp/pdfs/*.pdf cat output ./temp/network.pdf')

# converting pdf's to jpeg's using a shell script
# TODO: make a python module to convert such files into a movie clip

# pdftk *.pdf cat output 00.pdf
# #!/bin/bash
# for f in *.pdf; do
#   convert -density 300 -background white -alpha remove ./"$f" ./"${f%.pdf}.jpg"
# done


if __name__ == '__main__':
    main()

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
