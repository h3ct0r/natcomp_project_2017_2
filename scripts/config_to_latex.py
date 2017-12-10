#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import json
from pprint import pprint

# {
#   "dataset":"dataset/rescue1_50x50.json",
#   "ant_number": 100,
#   "alpha": 10,
#   "beta": 0.1,
#   "pheromone_evaporation_red": 0.001,
#   "pheromone_evaporation_blue": 0.01,
#   "pheromone_t0": 0.1,
#   "seed": 1,
#   "repetitions": 30,
#   "row_number": 200,
#   "col_number": 300,
#   "start_point": [0, 0]
# }

def prepare_latex_entry(title, data):
    template = """
\subsubsection{{{0}}}
	\\begin{{table}}[H]%Please add header.
		\centering
		\scriptsize
		\\begin{{minipage}}{{.4\\textwidth}}
			\centering
			\\begin{{tabular}}{{cc}}
				\\toprule
				\\textbf{{Parâmetro}} & \\textbf{{Valor}} \\\\ 
				\\bottomrule
				Numero de formigas & {1}\\\\
				$\\alpha$ & {2}\\\\
				$\\beta$ & {3}\\\\
				Evaporação vermelho & {4} \\\\
				Evaporação azul & {5} \\\\
				\\bottomrule
			\\end{{tabular}}
		\\end{{minipage}}
		%\\caption{{Parâmetros para a configuração: {0}.}}
		%\\label{{tab:}}
	\end{{table}}
    """

    print template.format(title, data["ant_number"],
                          data["alpha"],
                          data["beta"],
                          data["pheromone_evaporation_red"],
                          data["pheromone_evaporation_blue"])
    pass


def load_dataset_indexes(path):

    for root, dirs, files in os.walk(path):
        for name in files:
            if not name.endswith('.json'):
                continue

            full_path = os.path.join(root, name)
            data = json.load(open(full_path))
            prepare_latex_entry(name, data)

load_dataset_indexes("../config/")
