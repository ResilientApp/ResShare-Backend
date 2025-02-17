import requests

ipfs_cluster_api_url = None
ipfs_gateway_url = None


def read_config_file():
    """
    Reads the IPFS Cluster API URL and IPFS Gateway URL from the configuration file.
    Sets the values of global variables ipfs_cluster_api_url and ipfs_gateway_url.
    """
    global ipfs_cluster_api_url, ipfs_gateway_url
    with open("config/ipfs.config") as f:
        ipfs_cluster_api_url = f.readline().strip()
        ipfs_gateway_url = f.readline().strip()


def add_file_to_cluster(file_path):
    """
    Adds a file to the IPFS Cluster.

    :param file_path: The path to the file to be added.
    :return: The CID (Content Identifier) of the file if successful, otherwise None.
    """
    if ipfs_cluster_api_url is None or ipfs_gateway_url is None:
        read_config_file()

    url = ipfs_cluster_api_url + "add"
    files = {'file': open(file_path, 'rb')}
    response = requests.post(url, files=files)

    if response.status_code == 200:
        cid = response.json()['cid']['/']
        print(f"File added successfully with CID: {cid}")
        return cid
    else:
        print("Failed to add file to IPFS Cluster.")
        print(response.text)


def pin_file(cid, replication_min, replication_max):
    """
    Pins a file in the IPFS Cluster to ensure it remains available.

    :param cid: The CID of the file to be pinned.
    :param replication_min: The minimum number of replicas.
    :param replication_max: The maximum number of replicas.
    """
    if ipfs_cluster_api_url is None or ipfs_gateway_url is None:
        read_config_file()

    url = f"{ipfs_cluster_api_url}pins/{cid}"
    payload = {
        "replication-min": replication_min,
        "replication-max": replication_max
    }
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print(f"File with CID {cid} pinned successfully.")
    else:
        print("Failed to pin file to IPFS Cluster.")
        print(response.text)


def get_file_status(cid):
    """
    Retrieves the status of a file in the IPFS Cluster.

    :param cid: The CID of the file.
    :return: The status information of the file if successful, otherwise None.
    """
    if ipfs_cluster_api_url is None or ipfs_gateway_url is None:
        read_config_file()

    url = f"{ipfs_cluster_api_url}pins/{cid}"
    response = requests.get(url)

    if response.status_code == 200:
        file_info = response.json()
        return file_info
    else:
        print("Failed to get file status from IPFS Cluster.")
        print(response.text)


def download_file_from_ipfs(cid, save_path):
    if ipfs_cluster_api_url is None or ipfs_gateway_url is None:
        read_config_file()

    # Print the configuration to verify
    print(f"IPFS Cluster API URL: {ipfs_cluster_api_url}")
    print(f"IPFS Gateway URL: {ipfs_gateway_url}")

    url = f"{ipfs_gateway_url}ipfs/{cid}"
    print(f"Download URL: {url}")

    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(save_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"File downloaded successfully and saved to {save_path}")
            return {"success": True, "message": f"File downloaded successfully and saved to {save_path}"}
        else:
            error_message = f"Failed to download file. Status code: {response.status_code}. Response: {response.text}"
            print(error_message)
            return {"success": False, "message": error_message}
    except requests.exceptions.RequestException as e:
        error_message = f"Error downloading file from IPFS: {e}"
        print(error_message)
        return {"success": False, "message": error_message}


def list_pinned_files():
    """
    Retrieves information about all pinned files in the IPFS Cluster.

    :return: A list of information about pinned files if successful, otherwise None.
    """
    if ipfs_cluster_api_url is None or ipfs_gateway_url is None:
        read_config_file()

    url = f"{ipfs_cluster_api_url}pins"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            pinned_files = response.json()
            return pinned_files
        else:
            print(f"Failed to retrieve pinned files. Status code: {response.status_code}")
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to IPFS Cluster API: {e}")


def list_all_peers():
    """
    Retrieves information about all peers in the IPFS Cluster.

    :return: A list of information about all peers if successful, otherwise None.
    """
    if ipfs_cluster_api_url is None or ipfs_gateway_url is None:
        read_config_file()

    url = f"{ipfs_cluster_api_url}/peers"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            peers_info = response.json()
            return peers_info[0]
        else:
            print(f"Failed to retrieve peers info. Status code: {response.status_code}")
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to IPFS Cluster API: {e}")


def get_my_peer_id():
    """
    Retrieves the peer ID of the current IPFS Cluster peer.

    :return: The peer ID of the current IPFS Cluster node if successful, otherwise None.
    """
    if ipfs_cluster_api_url is None or ipfs_gateway_url is None:
        read_config_file()

    url = f"{ipfs_cluster_api_url}/id"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            peer_info = response.json()
            peer_id = peer_info.get('id')
            return peer_id
        else:
            print(f"Failed to retrieve peer ID. Status code: {response.status_code}")
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to IPFS Cluster API: {e}")



def get_peer_name(peer_id):
    """
    Fetch the peer name of a specific peer by its ID.

    :param api_url: The base URL of the IPFS Cluster API.
    :param peer_id: The peer ID of the target node.
    :return: The peer name if found, otherwise None.
    """
    url = f"{ipfs_cluster_api_url}/peers"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            peers = response.json()
            for peer in peers:
                if peer["id"] == peer_id:
                    return peer.get("peername", "Unknown Peername")
            print(f"Peer ID {peer_id} not found in the cluster.")
        else:
            print(f"Failed to fetch peers. Status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error fetching peername: {e}")
    return None
def remove_file_from_cluster(cid):
    """
    Removes a file from the IPFS Cluster.

    :param cid: The CID of the file to be removed.
    :return: True if the file is successfully removed, otherwise False.
    """
    if ipfs_cluster_api_url is None or ipfs_gateway_url is None:
        read_config_file()

    verify_url = f"{ipfs_cluster_api_url}/pins/{cid}"
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    verify_response = requests.get(verify_url, headers=headers)
    
    if verify_response.status_code == 404:
        print(f"CID {cid} not found in cluster")
        return False

    url = f"{ipfs_cluster_api_url}pins/{cid}"
    try:
        
        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            print(f"File with CID {cid} successfully removed from IPFS Cluster.")
            trigger_gc_on_nodes()
            print(f"File with CID {cid} successfully deleted from IPFS Cluster.")
            return True
        else:
            print(f"Failed to remove file with CID {cid}. Status code: {response.status_code}")
            print(response.text)
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error removing file from IPFS Cluster: {e}")
        return False
    
def trigger_gc_on_nodes():
    if ipfs_cluster_api_url is None or ipfs_gateway_url is None:
        read_config_file()
    
    gc_url = f"{ipfs_cluster_api_url}ipfs/gc?local=false"
    try:
        response = requests.post(gc_url)
        if response.status_code == 200:
            print("Garbage collection successfully triggered.")
        else:
            print(f"Failed to trigger GC. Status code: {response.status_code}")
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error triggering garbage collection: {e}")
