# -*- coding: utf-8 -*-
# @Time    : 3/28/2025 2:06 PM
# @Author  : yuzhounie
# @File    : example.py
# @Software: PyCharm
import dspy
from dotenv import load_dotenv
from dspy.datasets.gsm8k import GSM8K, gsm8k_metric

from dspy.evaluate import Evaluate

# Import the optimizer
from dspy.teleprompt import MIPROv2


class CoT(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.ChainOfThought("question -> answer")

    def forward(self, question):
        return self.prog(question=question)


if __name__ == "__main__":
    load_dotenv()
    dspy.configure(lm=dspy.LM('openai/gpt-4o-mini'))

    gsm8k = GSM8K()

    trainset, devset = gsm8k.train, gsm8k.dev
    program = CoT()

    evaluate = Evaluate(
        devset=devset[:],
        metric=gsm8k_metric,
        num_threads=8,
        display_progress=True,
        display_table=False,
    )
    evaluate(program, devset=devset[:])

    # Initialize optimizer
    teleprompter = MIPROv2(
        metric=gsm8k_metric,
        auto="light",  # Can choose between light, medium, and heavy optimization runs
    )

    # Optimize program
    print("Optimizing zero-shot program with MIPRO...")
    zeroshot_optimized_program = teleprompter.compile(
        program.deepcopy(),
        trainset=trainset,
        max_bootstrapped_demos=0,  # ZERO FEW-SHOT EXAMPLES
        max_labeled_demos=0,  # ZERO FEW-SHOT EXAMPLES
        requires_permission_to_run=False,
    )

    # Save optimize program for future use
    zeroshot_optimized_program.save("mipro_zeroshot_optimized.json")

    # Evaluate optimized program
    print("Evaluate optimized program...")
    evaluate(zeroshot_optimized_program, devset=devset[:])
