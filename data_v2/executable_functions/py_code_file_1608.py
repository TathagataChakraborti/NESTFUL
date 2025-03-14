from typing import List, Iterable



def list_chunks(lst: List[int], size: int = 2) -> List[List[int]]:

    """

    Returns a nested list of lists, where the first element is the list itself,

    followed by all sublists generated by successively splitting the list into

    chunks of the size of the first argument.



    Args:

        lst: The list to be split into chunks.

        size: The size of the chunks. Default is 2.

    """

    def chunks(lst: List[int], size: int) -> Iterable[List[int]]:

        for i in range(0, len(lst), size):

            yield lst[i:i + size]



    return [lst] + list(chunks(lst, size))

