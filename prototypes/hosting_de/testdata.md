# Test Data

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
  "complaint": "- At the garage entrance (directly below the garage door) several plates have dissolved. In the case of rains there are water entrances. - Parts of the northern side wall have moisture damage. This has already replaced paint, plaster and several edge tiles.",
  "problems": [
    "- Plates that have dissolved at the garage entrance (directly below the garage door)",
    "- Defective parts: The northern side wall has moisture damage, which has already replaced paint, plaster and several edge tiles."
  ],
  "prompt": "\n        You are a helpful problem identifier for a construction company.\n        Identify the problems the client expresses in the following complaint.\n        Since you are empathic, you want to understand the client's problems, no matter how they are expressed.\n\n        Original complaint:\n        ~~~\n        - At the garage entrance (directly below the garage door) several plates have dissolved. In the case of rains there are water entrances. - Parts of the northern side wall have moisture damage. This has already replaced paint, plaster and several edge tiles.\n        ~~~\n        Identify the defective components and assign the corresponding defect.\n        Do not add information not contained in the original complaint.\n        Do not draw any conclusions.\n\n        Problems:\n        ",
  "sentiment": "neutral"
}
~~~

*Query*

~~~json
{
  "step": "identify_problem",
  "complaint": "Wegen Ihrer Pfusch-Arbeit steht mein ganzes Haus unter Wasser!",
  "with_translation": "true",
  "with_sentiment": "true"
}
~~~

*Response*

~~~json
{
  "complaint": "- At the garage entrance (directly below the garage door) several plates have dissolved. In the case of rains there are water entrances. - Parts of the northern side wall have moisture damage. This has already replaced paint, plaster and several edge tiles.",
  "problems": [
    "- Plates that have dissolved at the garage entrance (directly below the garage door)",
    "- Defective parts: The northern side wall has moisture damage, which has already replaced paint, plaster and several edge tiles."
  ],
  "prompt": "\n        You are a helpful problem identifier for a construction company.\n        Identify the problems the client expresses in the following complaint.\n        Since you are empathic, you want to understand the client's problems, no matter how they are expressed.\n\n        Original complaint:\n        ~~~\n        - At the garage entrance (directly below the garage door) several plates have dissolved. In the case of rains there are water entrances. - Parts of the northern side wall have moisture damage. This has already replaced paint, plaster and several edge tiles.\n        ~~~\n        Identify the defective components and assign the corresponding defect.\n        Do not add information not contained in the original complaint.\n        Do not draw any conclusions.\n\n        Problems:\n        ",
  "sentiment": "neutral"
}
~~~

*Query*

