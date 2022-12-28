var setTableMaker = function functionSetTableMaker(setVars)

{

  var tabledata = setVars.tabledata;
  console.log('tabledata = ')
  console.log(tabledata)

  var divName = "#" + setVars.divName
  console.log('divName  = ')
  console.log(divName)

  var filename = setVars.divName
  console.log('filename = ')
  console.log(filename)

  var button_name = "download-csv-" + setVars.divName
  console.log('button_name = ')
  console.log(button_name)

  var table = new Tabulator(divName, {
      data:tabledata,           //load row data from array
      layout:"fitColumns",      //fit columns to width of table
      responsiveLayout:"hide",  //hide columns that dont fit on the table
      tooltips:true,            //show tool tips on cells
      addRowPos:"top",          //when adding a new row, add it to the top of the table
      history:true,             //allow undo and redo actions on the table
      pagination:"local",       //paginate the data
      paginationSize:10,         //allow 7 rows per page of data
      paginationCounter:"rows", //display count of paginated rows in footer
      movableColumns:true,      //allow column order to be changed
      initialSort:[             //set the initial sort order of the data
          {column:"Condition Name", dir:"asc"},
      ],
      columns:[                 //define the table columns
          {title:"word", field:"word", editor:"input"},
          {title:"count", field:"count", width:100, editor:"input", bottomCalc:"sum", bottomCalcParams:{precision:0}},
          {title:"percent", field:"percent", width:100, editor:"input", bottomCalc:"sum", bottomCalcParams:{precision:0}},
        //  {title:"Task Progress", field:"progress", hozAlign:"left", formatter:"progress", editor:true},
        //  {title:"Gender", field:"gender", width:95, editor:"select", editorParams:{values:["male", "female"]}},
        //  {title:"Rating", field:"rating", formatter:"star", hozAlign:"center", width:100, editor:true},
          //{title:"Color", field:"col", width:130, editor:"input"},
          //{title:"Date Of Birth", field:"dob", width:130, sorter:"date", hozAlign:"center"},
          //{title:"Driver", field:"car", width:90,  hozAlign:"center", formatter:"tickCross", sorter:"boolean", editor:true},
      ],
  });



  //trigger download of data.xlsx file
  document.getElementById(button_name).addEventListener("click", function(){
      table.download("csv", filename);
  });



};
