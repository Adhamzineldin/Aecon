if(localStorage && !localStorage.schoolstreets){
    console.log("creating storage!")
    createStorage();
}

function createStorage(){
    var limits = {"CO":[0.15,false],"NO":[200,false],"NO2":["100",false],"Temp":[30,false],"Noise":[100,false]}
    var selectedClasses = getSelectedPopupIndexes("classes-popup");
    var localStorageData = {"limits":limits,"selectedClasses":selectedClasses,"email":"","selectedSites":{1:[],2:[],3:[],4:[],5:[],6:[]}};
    save(localStorageData);
}

function saveClassesToLocalStorage(classIndexes){
    var data = loadLocalStorage();
    data.selectedClasses = classIndexes;
    save(data);
}

function saveLimitsToLocalStorage(limits){
    var data = loadLocalStorage();
    data.limits = limits;
    save(data);
}

function getLimits(){
    var data = loadLocalStorage();
    return data.limits;
}


function saveSitesToLocalStorage(obsType,sites){
    var data = loadLocalStorage();
    console.log("sites are",sites)
    console.log("in storage",data.selectedSites)
    console.log("in storage",data.selectedSites[obsType]);
    data.selectedSites[obsType] = sites;
    save(data);
}

function getSitesFromLocalStorage(obsType){
    var data = loadLocalStorage();
    console.log("data is",data);
    console.log("sites are",data.selectedSites,typeof data.selectedSites)

    var sites = data.selectedSites[obsType]
    return sites;
}

function save(data){
    localStorage.setItem("schoolstreets",JSON.stringify(data));
}

function loadLocalStorage(){
    var data = JSON.parse(localStorage.getItem("schoolstreets"));
    return data
}