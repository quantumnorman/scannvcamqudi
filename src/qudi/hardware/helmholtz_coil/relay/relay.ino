
int OPpins[] = {7,8,9,10,11,12}; //inputs x,y,z are pins 7,8,9; outputs are 10,11,12

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  for (int i = 0; i<6;i++)
  {
    pinMode(OPpins[i], OUTPUT);
  }

}

void serialEvent(){
  int stri,strl;
  String strread,strwrite,pini,stati,mode;
  pini=-999;
  stati=-999;
  //statements
  strread = Serial.readStringUntil('\n');
  stri=strread.indexOf(' ');
  strl=strread.length();
//  strwrite="Error";
//  strwrite=(String(stri));

  //select mode
  mode=strread.substring(0,stri);//mode
  Serial.print("Mode:");
  Serial.print(mode);
  Serial.print("\n");


  //select pin and output
  strread=strread.substring(stri+1,strl);//read substring for pins
  strwrite=strread;
  Serial.print("Values read:");
  Serial.print(strread);
  Serial.print("\n");
  stri=strread.indexOf(' ');
  strl=strread.length();
  Serial.print("stri:");
  Serial.print(stri);
  Serial.print("strl:");
  Serial.print(strl);
  //strwrite=mode;

    if (mode=="set"){
        if (stri==1) {
            pini=strread.substring(0,stri);//pin number
            stati=strread.substring(stri+1,strl);//Status of pin
            if (((stati.toInt()==1)||(stati.toInt()==0))&&(pini.toInt()>=0)&&(pini.toInt()<=2)){
              strwrite="pin:"+String(OPpins[pini.toInt()*2])+" status:"+String(stati);
              strwrite=strwrite+'\n'+"pin:"+String(OPpins[pini.toInt()*2+1])+" status:"+String(stati);
              setPin(OPpins[pini.toInt()*2],stati.toInt()==1);
              setPin(OPpins[pini.toInt()*2+1],stati.toInt()==1);
           }
        }

    }
    else if (mode=="get"){
      //strwrite=String(stri);
      if (stri==-1){
        pini=strread.substring(0,1);//pin number
        strwrite=pini;
        if ((pini.toInt()>=0)&&(pini.toInt()<=2)){
          strwrite="output:"+String(pini.toInt())+" status:"+String(digitalRead(OPpins[pini.toInt()*2]));
        }
      }
    }
    else{
    }
  
//  if (stri==2) {
//    pini=strread.substring(0,stri);//pin number
//    stati=strread.substring(stri+1,strl);//Status of pin
//    if (((stati.toInt()==1)||(stati.toInt()==0))&&(pini.toInt()>=0)&&(pini.toInt()<=2)){
//      
//      strwrite="pin:"+String(OPpins[pini.toInt()*2])+" status:"+String(stati);
//      strwrite=strwrite+'\n'+"pin:"+String(OPpins[pini.toInt()*2+1])+" status:"+String(stati);
//      setPin(OPpins[pini.toInt()*2],stati.toInt()==1);
//      setPin(OPpins[pini.toInt()*2+1],stati.toInt()==1);
//    
//    }
//  }

  
  Serial.println(strwrite+'\n');
}

void loop() {
  // put your main code here, to run repeatedly:

}

void setPin(int pinId, bool stat) {
  digitalWrite(pinId, stat);
}
