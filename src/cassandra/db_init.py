from argparse import ArgumentParser
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider


"""
python3 db_init.py -i localhost -p 9042 -k zenprice -s pickle_data -u pickle_data_unique -d pickle_results
"""

if __name__ == "__main__":
    # parse arguments (files, cluster_ip, etc)
    parser = ArgumentParser()
    parser.add_argument("-i", "--ip", default="127.0.0.1")
    parser.add_argument("-p", "--port", default=9042)
    parser.add_argument("-k", "--keyspace", default="zenprice")
    parser.add_argument("-s", "--source", default="pickle_data")
    parser.add_argument("-u", "--unique", default="pickle_data_unique")
    parser.add_argument("-d", "--destination", default="pickle_results")
    args = parser.parse_args()

    # create session
    auth_provider = PlainTextAuthProvider(username="cassandra", password="cassandra")

    print(f"CONNECTING TO '{args.ip}:{args.port}'...")
    cluster = Cluster([args.ip], port=args.port, auth_provider=auth_provider)
    session = cluster.connect()

    # create keyspace
    print(f"CREATING KEYSPACE '{args.keyspace}'...")
    session.execute(
        "CREATE KEYSPACE IF NOT EXISTS "
        + args.keyspace
        + " WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 3 };"
    )

    # create table
    print(f"CREATING TABLES...")
    rows = session.execute(
        f"SELECT table_name FROM system_schema.tables WHERE keyspace_name='{args.keyspace}';"
    )
    flag = False
    for row in rows:
        if args.source in row or args.destination in row or args.unique in row:
            print("TABLE ALREADY EXISTS.")
            flag = True

    if flag is False:
        print("TABLE DOES NOT EXIST.\nCREATING TABLE...")
        session.execute(
            f"CREATE TABLE IF NOT EXISTS {args.keyspace}.{args.source} \
                        (id uuid PRIMARY KEY, \
                        timestamp timestamp, \
                        product_id int, \
                        model varchar, \
                        country varchar, \
                        company varchar, \
                        product_group_id int, \
                        subscription varchar, \
                        price float);"
        )

        session.execute(
            f"CREATE TABLE IF NOT EXISTS {args.keyspace}.{args.unique} \
                        (id uuid PRIMARY KEY, \
                        timestamp timestamp, \
                        product_id int, \
                        model varchar, \
                        country varchar, \
                        company varchar, \
                        product_group_id int, \
                        subscription varchar, \
                        price float);"
        )

        session.execute(f"CREATE TABLE  IF NOT EXISTS {args.keyspace}.{args.destination} \
                                (product_id int PRIMARY KEY, \
                                timestamp timestamp, \
                                model varchar, \
                                country varchar, \
                                company varchar, \
                                subscription varchar, \
                                prediction list<float>);")

        print("TABLE CREATED.")

    print("CREATING USER FOR CRONJOBS...")
    # Create the role with read and write permissions
    session.execute(
        f"CREATE ROLE IF NOT EXISTS 'cron_user' WITH PASSWORD = 'cron_password' AND LOGIN = true"
    )

    # Grant read and write permissions on the keyspace to the role
    session.execute(f"GRANT SELECT ON KEYSPACE zenprice TO cron_user;")
    session.execute(f"GRANT MODIFY ON KEYSPACE zenprice TO cron_user;")

    session.shutdown()
    cluster.shutdown()

    print("EVERYTHING CREATED.\nEXITING...")
