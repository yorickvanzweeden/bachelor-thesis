package nl.yorickvanzweeden.helloworld;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

public class HelloReceiver extends BroadcastReceiver {
    public static final String ACTION_SAY_HELLO = "nl.yorickvanzweeden.intent.action.SAY_HELLO";

    @Override
    public void onReceive(Context context, Intent intent) {
        new ToastDisplay(context, intent.getStringExtra("message"));
    }
}
