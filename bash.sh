#!/usr/bin/bash
curl  -X POST -H "Content-Type:application/json" -d \
'{"description":"Rent","amount":400}' http://127.0.0.1:5000/expenses
