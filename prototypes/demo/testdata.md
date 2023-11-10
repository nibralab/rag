# Test Data

*Query*

~~~json
{
  "step": "rephrase",
  "input": "Wegen Ihrer Pfusch-Arbeit steht mein ganzes Haus unter Wasser! Außerdem schließt die Haustür nicht ordentlich.",
  "with_translation": "true",
  "with_sentiment": "true"
}
~~~

*Response*

~~~json
{
    "answer": [
        "* Water damage in the house.",
        "* Front door does not close properly."
    ],
    "input": "Because of your fuss work, my whole house is under water, and the front door doesn't close properly.",
    "prompt": "\n        You are a helpful fact-oriented assistant.\n        Extract the problems behind the complaint.\n        Keep the meaning of the input text. NEVER ADD OR REMOVE ANY INFORMATION.\n        USE SIMPLE LANGUAGE WITHOUT SUBORDINATE CLAUSES.\n        Instead of \"The problem behind the complaint is that <problem>.\", write \"<problem>.\"\n        Identify all problems. Output one problem per line.\n        Don't presume anything. If no problems are stated explicitly, don't add them.\n\n        Input text:\n        \"Because of your fuss work, my whole house is under water, and the front door doesn't close properly.\"\n        \n        Output text:\n        ",
    "sentiment": "disappointment"
}
~~~

*Query*

