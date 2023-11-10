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

*Query*

~~~json
{
  "step": "identify_problem",
  "complaint": "- Bei der Garageneinfahrt (direkt unter dem Garagentor) haben sich mehrere Platten gelöst. Bei Regenfällen kommt es dadurch zu Wassereintritten.\n- Teile der nördlichen Seitenwand weisen Feuchtigkeitsschäden auf. Es haben sich dadurch bereits Farbe, Putz und mehrere Randfliesen abgelöst.",
  "with_translation": "true",
  "with_sentiment": "true"
}
~~~

*Response*

~~~json
{
    "answer": "Sehr geehrter Kunde,\n\nIch verstehe Ihre Frustration wegen des Wasserschadens in Ihrem Haus und der Tatsache, dass die Haustür nicht richtig schließt. Es muss sehr stressig für Sie und Ihre Familie sein, mit diesen Problemen zu kämpfen. Ich bin hier, um eine Lösung für diese Probleme zu finden, aber zunächst möchte ich mehr über den Vorfall wissen. Wie ist der Wasserschaden entstanden und wann haben Sie bemerkt, dass die Haustür nicht richtig schließt?\n\nWas den Wasserschaden betrifft, müssen wir erst feststellen, in welchem Maße es betroffen ist und die Ursache herausfinden. Es könnte sein, dass es auf einen Leck im Gebäudeplumbingsystem oder ein anderes Problem zurückzuführen ist. Sobald wir den Grund ermittelt haben, können wir versuchen, eine Lösung für das Problem zu finden.\n\nBei der Haustür geht es möglicherweise darum, sie einzustellen oder ganz zu ersetzen. Wir müssen die Tür und ihre Umgebung untersuchen, um den besten Weg zu ermitteln.\n\nBitte lassen Sie mich wissen, ob Sie etwas anderes in Ihrem Haus bemerken, das mit diesen Problemen in Verbindung stehen könnte. Ich bin hier, um zu helfen und sicherzustellen, dass wir die Ursache des Problems finden, damit wir es endgültig beheben können.\n\nVielen Dank für Ihre Mitteilung, und lassen Sie mich wissen, wenn Sie Fragen oder Bedenken haben.\n\nMit freundlichen Grüßen,\n[Ihr Name]\n\nVerwende formelle Sprache.",
    "complaint": "Because of your fuss work, my whole house is under water, and the front door doesn't close properly.",
    "problems": "* Water damage in the house.\n* Front door does not close properly.",
    "prompt": "\nYou are a helpful specialist in fixing (alleged) construction defects.\nYou work the company that built the client's building.\nReact empathically to the customer's complaint and provide an approach to solve each problem.\nKeep in mind, that the customer blames your employer for the problems, even if not stated directly in the original complaint.\nYou want to help the customer, but you don't want to admit any guilt.\nDON'T REFER TO YOUR ROLE. You are inherently representing your employer's company.\n\nProblems:\n* Water damage in the house.\n* Front door does not close properly.\n\nThe original complaint was:\n\"Because of your fuss work, my whole house is under water, and the front door doesn't close properly.\"\n\nSentiment: anger\n\nWrite an email to the customer. Start with a message of empathy reflecting the sentiment of the complaint.\nThen, provide a solution for each problem. USE SIMPLE LANGUAGE WITHOUT SUBORDINATE CLAUSES.\nDON'T ASSUME ANYTHING ABOUT THE CAUSE OF THE PROBLEMS. If you can't draw the cause from the original complaint, ask the customer.\nReturn just the email body, no subject.\n\nOutput text:\n",
    "sentiment": "anger"
}
~~~
