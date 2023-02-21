# Build RAFT algorithm
import xmlrpc

from network.client import Client


def main():
    """Main function."""
    client = Client("localhost", 8080)
    client.set("foo", "bar")
    print(client.get("foo"))


if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
