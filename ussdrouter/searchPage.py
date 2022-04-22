def Page(str, keyword='#', page=1):

  strArray = str.split('*')

  for i in range(len(strArray)):
    
    if strArray[i][:1] == keyword:
      page = strArray[i][1:]
    else:
      page = 1

  return int(page)