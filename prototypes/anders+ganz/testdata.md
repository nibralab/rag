# Test Data

*Query*

~~~json
{
  "step": "identify_problem",
  "complaint": "Wegen Ihrer Pfusch-Arbeit steht mein ganzes Haus unter Wasser! Außerdem schließt die Haustür nicht ordentlich.",
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
    "complaint": "Because of your fuss work, my whole house is under water, and the front door doesn't close properly.",
    "prompt": "\n        You are a helpful fact-oriented assistant.\n        Extract the problems behind the complaint.\n        Keep the meaning of the input text. NEVER ADD OR REMOVE ANY INFORMATION.\n        USE SIMPLE LANGUAGE WITHOUT SUBORDINATE CLAUSES.\n        Instead of \"The problem behind the complaint is that <problem>.\", write \"<problem>.\"\n        Identify all problems. Output one problem per line.\n        Don't presume anything. If no problems are stated explicitly, don't add them.\n\n        Input text:\n        \"Because of your fuss work, my whole house is under water, and the front door doesn't close properly.\"\n        \n        Output text:\n        ",
    "sentiment": "disappointment"
}
~~~

## Wasserschäden

### Problem-Erkennung

*Query*

~~~json
{
  "step": "identify_problem",
  "complaint": "Bei der Garageneinfahrt (direkt unter dem Garagentor) haben sich mehrere Platten gelöst. Bei Regenfällen kommt es dadurch zu Wassereintritten.\n- Teile der nördlichen Seitenwand weisen Feuchtigkeitsschäden auf. Es haben sich dadurch bereits Farbe, Putz und mehrere Randfliesen abgelöst.",
  "with_translation": "true",
  "with_sentiment": "true"
}
~~~

*Response*

~~~json
{
    "complaint": "At the garage entrance (directly under the garage gate) several plates have dissolved. In case of rainfall there are water intrusions.\\n- Parts of the north side wall show moisture damage. It has already dissolved paint, plaster and several edge tiles. \\n",
    "problems": [
        "<Problem 1> The plates under the garage gate have dissolved.",
        "<Problem 2> There are water intrusions in case of rainfall.",
        "<Problem 3> Parts of the north side wall show moisture damage, including dissolved paint, plaster, and edge tiles."
    ],
    "prompt": "\nYou are a helpful fact-oriented assistant.\nExtract the problems behind the complaint.\nKeep the meaning of the input text. NEVER ADD OR REMOVE ANY INFORMATION.\nUSE SIMPLE LANGUAGE WITHOUT SUBORDINATE CLAUSES.\nInstead of \"The problem behind the complaint is that <problem>.\", write \"<problem>.\"\nIdentify all problems. Output one problem per line.\nDon't presume anything. If no problems are stated explicitly, don't add them.\n\nInput text:\n\"At the garage entrance (directly under the garage gate) several plates have dissolved. In case of rainfall there are water intrusions.\\n- Parts of the north side wall show moisture damage. It has already dissolved paint, plaster and several edge tiles. \\n-\"\n\nOutput text:\n",
    "sentiment": null
}
~~~

### Lösungsvorschläge

