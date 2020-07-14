window.onload=function(){
  var productItems = document.getElementsByClassName('productItems')

  var i = 0;
  for( i=0; i<16 && i<productItems.length; i++ ) {
    productItems[i].style.display = 'block'
  }

  var maxPage = 1;
   if( productItems.length<=16 ) {
     document.getElementById('pageCount').textContent = 'Page 1 of 1'
     document.getElementById('p2').style.display = 'none';
     document.getElementById('p3').style.display = 'none';
     document.getElementById('p4').style.display = 'none';
     document.getElementById('p5').style.display = 'none';
   } else if ( productItems.length<=32 ) {
     maxPage = 2;
     document.getElementById('pageCount').textContent = 'Page 1 of 2'
     document.getElementById('p3').style.display = 'none';
     document.getElementById('p4').style.display = 'none';
     document.getElementById('p5').style.display = 'none';
   } else if ( productItems.length<=48 ) {
     maxPage = 3;
     document.getElementById('pageCount').textContent = 'Page 1 of 3'
     document.getElementById('p4').style.display = 'none';
     document.getElementById('p5').style.display = 'none';
   } else if ( productItems.length<=64 ) {
     maxPage = 4;
     document.getElementById('pageCount').textContent = 'Page 1 of 4'
     document.getElementById('p5').style.display = 'none';
   } else if ( productItems.length<=80 ) {
     maxPage = 5;
     document.getElementById('pageCount').textContent = 'Page 1 of 5'
   }

   document.getElementById('p1').addEventListener('click', () => {
     document.getElementById('pageCount').textContent = 'Page 1 of '+ maxPage.toString()
     var i = 0;
     for( i=0; i<productItems.length; i++ ) {
       productItems[i].style.display = 'none'
     }
     for( i=0; i<16 && i<productItems.length; i++ ) {
       productItems[i].style.display = 'block'
     }
   })

   document.getElementById('p2').addEventListener('click', () => {
     document.getElementById('pageCount').textContent = 'Page 2 of '+ maxPage.toString()
     var i = 16;
     for( i=0; i<productItems.length; i++ ) {
       productItems[i].style.display = 'none'
     }
     for( i=16; i<32 && i<productItems.length; i++ ) {
       productItems[i].style.display = 'block'
     }
   })

   document.getElementById('p3').addEventListener('click', () => {
     document.getElementById('pageCount').textContent = 'Page 3 of '+ maxPage.toString()
     var i = 32;
     for( i=0; i<productItems.length; i++ ) {
       productItems[i].style.display = 'none'
     }
     for( i=32; i<48 && i<productItems.length; i++ ) {
       productItems[i].style.display = 'block'
     }
   })

   document.getElementById('p4').addEventListener('click', () => {
     document.getElementById('pageCount').textContent = 'Page 4 of '+ maxPage.toString()
     var i = 48;
     for( i=0; i<productItems.length; i++ ) {
       productItems[i].style.display = 'none'
     }
     for( i= 48; i<64 && i<productItems.length; i++ ) {
       productItems[i].style.display = 'block'
     }
   })

   document.getElementById('p5').addEventListener('click', () => {
     document.getElementById('pageCount').textContent = 'Page 5 of '+ maxPage.toString()
     var i = 64;
     for( i=0; i<productItems.length; i++ ) {
       productItems[i].style.display = 'none'
     }
     for( i=64; i<80 && i<productItems.length; i++ ) {
       productItems[i].style.display = 'block'
     }
   })

   document.getElementById('pnext').addEventListener('click', () => {
     pageNo = parseInt(document.getElementById('pageCount').textContent[5])
     if( pageNo != 5 && pageNo != maxPage ) {
       document.getElementById('p'+(pageNo+1).toString()).click();
     }
   })

   document.getElementById('pprevious').addEventListener('click', () => {
     pageNo = parseInt(document.getElementById('pageCount').textContent[5])
     if( pageNo != 1 ) {
       document.getElementById('p'+(pageNo-1).toString()).click();
     }
   })
}
