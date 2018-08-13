package nl.yorickvanzweeden.helloworld;

import android.content.Context;
import android.widget.Toast;

class ToastDisplay {
    ToastDisplay(Context context, String name){
        Toast.makeText(context, name + " says Hello!", Toast.LENGTH_SHORT).show();
    }
}
