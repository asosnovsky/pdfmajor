class PDFItem: 
    def __repr__(self) -> str:
        return f"""<{self.__class__.__name__} {' '.join([
            f'{name}="{val}"'
            for name, val in vars(self).items()
        ])}/>"""
