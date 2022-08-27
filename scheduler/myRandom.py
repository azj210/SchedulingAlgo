class Random:
    def __init__(self):
        self.RandomList = []
        self.index = -1
        with open("random-numbers.txt") as random_file:
            for line in random_file:
                self.RandomList.append(int(line))

    def randomOS(self, U):
        self.index += 1
        # print(self.RandomList[self.index])
        return 1 + self.RandomList[self.index] % U
