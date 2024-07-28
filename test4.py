from scholarly import scholarly

# Searching by keyword
search_query = "KAN"
search_results = scholarly.search_pubs(search_query)

# Print the titles of the first 5 results
for i in range(1):
    result = next(search_results)
    # print(result['bib']['title'])
    print(result.keys())

# # Searching by author
# author_name = "Andrew Ng"
# author_search = scholarly.search_author(author_name)
# author = next(author_search).fill()
# print(f"Author: {author.name}, Affiliation: {author.affiliation}")
#
# # Print the titles of the first 5 papers by this author
# for publication in author.publications[:5]:
#     print(publication.bib['title'])
