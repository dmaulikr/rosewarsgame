package com.wotr.strategy.impl;

import java.util.ArrayList;
import java.util.List;

import com.wotr.model.unit.Unit;
import com.wotr.model.unit.basic.Archer;
import com.wotr.model.unit.basic.Ballista;
import com.wotr.model.unit.basic.Catapult;
import com.wotr.model.unit.basic.HeavyCavalry;
import com.wotr.model.unit.basic.LightCavalry;
import com.wotr.model.unit.basic.Pikeman;
import com.wotr.model.unit.special.Berserker;
import com.wotr.model.unit.special.Chariot;
import com.wotr.strategy.DeckDrawStrategy;

public class FixedDeckDrawStrategy implements DeckDrawStrategy {

	@Override
	public List<Unit> drawDeck() {
		List<Unit> result = new ArrayList<Unit>();

		result.add(new Archer());
		result.add(new Archer());
		result.add(new Ballista());
		result.add(new Catapult());
		result.add(new HeavyCavalry());
		result.add(new LightCavalry());
		result.add(new Pikeman());
		result.add(new Berserker());
		result.add(new Chariot());

		return result;
	}

}
