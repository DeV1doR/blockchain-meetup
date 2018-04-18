# blockchain-meetup

```bash
    mkvirtualenv -p python3 bm
    pip install -r requirements.txt

    # creation/generation of private/public/address
    python m1_pk_2_pb_2_addr.py

    # send simple payload to the node
    python m2_send_simple_transaction.py

    # send offline payload to the node
    python m3_send_offline_transaction.py

    # execute some contract method
    python m4_execute_contract_method.py

    # decode event logs
    python m5_decode_event_logs.py
```