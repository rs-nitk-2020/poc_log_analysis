import os


class FileOps:
    """
    This class has methods for file and directory operations.
    """

    def create_dir(dir_path: str)->None:
        """
        Creates a directory at specified path if it doesnt exist

        Args:
            dir_path (str): path of the directory to be created.
        """        
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
