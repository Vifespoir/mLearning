console.log('Button clicked: %d', button.clicks)

    var myKeys = Object.keys(checkbox.callback.args)
    myKeys = myKeys.slice(2)
    var myKeyDict = {}
    for (index = 0; index < myKeys.length; index++) {
        var key = myKeys[index]
        myKeyDict[parseInt(key.substring(1))] = key
    }
    var myIndex = []
    for (key in Object.keys(myKeyDict)) {
        myIndex.push(parseInt(key))
    }
    console.log('myKeyDict')
    console.log(myKeyDict)
    console.log('myIndex')
    console.log(myIndex)
    console.log('checkbox.active')
    console.log(checkbox.active)
    if (button.clicks % 2 == 1) {

        for (index in myKeyDict) {
            console.log(checkbox.callback.args[myKeyDict[index]].visible)
            checkbox.callback.args[myKeyDict[index]].visible = false
        }
        checkbox.active = []
    }
    else {
        for (index in myKeyDict) {
            console.log(checkbox.callback.args[myKeyDict[index]].visible)
            checkbox.callback.args[myKeyDict[index]].visible = true
            }
        checkbox.active = myIndex
    }
