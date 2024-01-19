import requests
import streamlit as st

NOTION_API_KEY = st.secrets['database']['notion_secret_key']


# Function to fetch contents from notion server
def _fetch_block_contents(block_id,include_childrens=False):
    if include_childrens==False:
        # Fetch the block contents
        url = f'https://api.notion.com/v1/blocks/{block_id}'
        headers = {
            'Authorization': f'Bearer {NOTION_API_KEY}',
            'Notion-Version': '2022-06-28'
        }

        response = requests.get(url, headers=headers)
        return response.json()
    else:
        # Returns the list of children blocks
        # Fetches all the childrens of the given block
        # Later might need to do in chunkds and return the merged json
        # Only append the 'results' from multiple calls
        url = f'https://api.notion.com/v1/blocks/{block_id}/children'
        headers = {
            'Authorization': f'Bearer {NOTION_API_KEY}',
            'Notion-Version': '2022-06-28'
        }
        response = requests.get(url, headers=headers)
        return response.json()['results']

# Function to extract plain text from responst for one block from above
def __extract_block_content(block_dict):
    """
    input: block dictionary
    output: the plain text content of the block
    """
    btype = block_dict['type']
    content = block_dict[btype]
    block_content = " ".join([apart['plain_text'] for apart in content['rich_text']])
    return block_content

# Function to parse list of child blocks
def _extract_all_child_block_contents(child_block_list,prefix):
    """
    input: list of child block dicts
    output: string with adjusted indent
    """
    full_content = ""
    
    for block in child_block_list:    
        block_content = __extract_block_content(block)
        full_content = f"{full_content}{prefix}{block_content}"

        if block['has_children']:
            current_block_id = block['id']
            list_of_children_blocks = _fetch_block_contents(current_block_id,include_childrens=True)            
            child_contents = _extract_all_child_block_contents(list_of_children_blocks,
                                                          prefix = prefix + '--')
            
            full_content = f"{full_content}\n{child_contents}"
        else:
            full_content = f"{full_content}\n"
    return full_content

def _get_blockID_from_URL(full_url):
    """
    returns the block-id from the link to block
    """
    return full_url.split("?pvs=4#")[1]

@st.cache_data
def get_block_content(full_URL):
    """
    input: the copy link to block from notion UI
    output: title with all the children contents
    """
    blockID = _get_blockID_from_URL(full_URL)

    block_content = _fetch_block_contents(blockID,include_childrens=False)
    block_with_childrens = _fetch_block_contents(blockID,include_childrens=True)
    
    parent_block_id = block_content['parent']['page_id']
    parent_block_json = _fetch_block_contents(parent_block_id,include_childrens=False)
    class_title = parent_block_json['child_page']['title']
    
    title = __extract_block_content(block_content)
    children_contents = _extract_all_child_block_contents(block_with_childrens,prefix="")
    
    return {
            'class_title':class_title,
            "heading":title,
            "content":children_contents[:-1],
            'URL':full_URL}