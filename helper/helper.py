from pathlib import Path

import matplotlib.pyplot as plt
from IPython import display

# plt.ion()


def plot(scores: int, mean_scores: float, output_model_file: str, output_figure_dir: str = './figure'):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Training...')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))

    # output figure
    fig = plt.gcf()
    output_figure_dir_path = Path(output_figure_dir)
    output_figure_dir_path.mkdir(exist_ok=True)
    output_figure_name = Path(output_model_file).stem
    output_figure_path = output_figure_dir_path / f'{output_figure_name}.png'
    fig.savefig(output_figure_path)

    plt.show(block=False)
    plt.pause(.01)
