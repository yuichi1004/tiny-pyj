tiny-pyj
========
Tiny JSON RPC 2.0 Client for Python

Overview
-------
tiny-pyj is a JSON RPC 2.0 client library for python. The goal of this project 
is minimal JSON rpc client which can easily linked to any project with minimal
dependencies.


Usage
-------
tiny-pyj is a single python file. tiny-pyj can be copied, be imported as part
of your software distribution

    import tinypyj
	smd = open('./example.smd.json').read()
	c = tinypyj.Client(smd, 'http://localhost')
	print c.add(1, 3)	# will print 4


SMD
------
tiny-pyj loads SMD json file. The following is the example format of smd JSON.

    {
    	"target": "/jsonrpc",
    	"transport": "POST",
    	"services": {
    	    "add": {
    	        "parameters": [
    	            {"type": "integer", "name":"a", "optional":false},
    	            {"type": "integer", "name":"b", "optional":false},
    	            {"type": "integer", "name":"c", "optional":true}
    	        ],
    	        "returns": {"type":"integer"}
    	    },
    	}
    }


Test
------
Unit tests available on test.py

    python test.py

Licsense
-------
This software is available under MIT License.

