package com.openclaw.androidecosystem.contacts

import android.widget.SeekBar

class SimpleSeekBarChangeListener(
    private val onProgressChanged: (Int) -> Unit
) : SeekBar.OnSeekBarChangeListener {
    override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
        onProgressChanged(progress)
    }

    override fun onStartTrackingTouch(seekBar: SeekBar?) = Unit

    override fun onStopTrackingTouch(seekBar: SeekBar?) = Unit
}
