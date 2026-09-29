import json

def get_unfollowers(followers_file, following_file):

    #load json data
    with open(followers_file,'r')as f1, open (following_file, 'r')as f2:

         followers_data= json.load(f1)
         following_data=json.load(f2)

    #extract usernames to python sets for comparison
    followers= {user['string_list_data'][0]['value'] for user in followers_data}
    following= {user['string_list_data'][0]['value'] for user in following_data['relationships_following']}

    #se who is in following not on followers
    unfollowers= following- followers

    return unfollowers

