package nl.yorickvanzweeden.helloworld;

import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.ServiceConnection;
import android.os.Bundle;
import android.os.IBinder;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.Toast;


public class MainActivity extends AppCompatActivity {
    private HelloReceiver helloReceiver;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);


        findViewById(R.id.button_start).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startService();
                findViewById(R.id.button_start).setEnabled(false);
                findViewById(R.id.button_stop).setEnabled(true);
            }
        });

        findViewById(R.id.button_stop).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                stopService();
                findViewById(R.id.button_start).setEnabled(true);
                findViewById(R.id.button_stop).setEnabled(false);
            }
        });

        findViewById(R.id.button_startActivity).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent i = new Intent();
                i.setAction("nl.yorickvanzweeden.intent.action.SECOND_ACTIVITY");
                i.setType("text/plain");
                startActivity(i);
            }
        });
    }

    @Override
    protected void onStart() {
        super.onStart();
        helloReceiver = new HelloReceiver();
        IntentFilter intentFilter = new IntentFilter(HelloReceiver.ACTION_SAY_HELLO);
        this.registerReceiver(helloReceiver, intentFilter);
    }

    @Override
    protected void onStop() {
        super.onStop();
        this.unregisterReceiver(helloReceiver);
    }

    private void startService(){
        Intent i = new Intent();
        i.setClass(this, HelloService.class);
        this.startService(i);
    }

    private void stopService(){
        stopService(new Intent(this, HelloService.class));
    }
}
